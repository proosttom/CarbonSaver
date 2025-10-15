"""
CarbonSaver Flask API
Provides endpoints for carbon intensity forecasting and load optimization
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
from elia_forecast import build_carbon_intensity_forecast_from_elia
from load_optimizer import (
    compare_load_profiles,
    find_optimal_timeslot,
    calculate_load_emissions,
)

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)  # Enable CORS for all routes


@app.route("/")
def index():
    """Serve the main HTML page.

    Returns:
        Response: The index.html file from the static directory.
    """
    return send_from_directory("static", "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JS, images, etc.).

    Args:
        filename (str): The path to the static file relative to the static directory.

    Returns:
        Response: The requested static file.
    """
    return send_from_directory("static", filename)


@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    """Get carbon intensity forecast for a specific date.

    Fetches hourly carbon intensity forecast data from Elia's open data platform,
    including load, renewable generation, and calculated carbon intensity values.

    Query Parameters:
        date (str, optional): Date in YYYY-MM-DD format. If not provided, uses the most
                             recent date with available data.

    Returns:
        Response: JSON object containing:
            - success (bool): Whether the request succeeded
            - summary (dict): Summary statistics including min/max/avg carbon intensity,
                            date, and total hours
            - hourly_data (list): List of hourly forecast records with datetime, load,
                                 renewables, and carbon intensity values

        Status Codes:
            200: Success
            400: Invalid date format
            500: Could not fetch forecast data
    """
    try:
        # Get optional date parameter
        date_str = request.args.get("date")
        use_date = None

        if date_str:
            try:
                use_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Get forecast
        forecast_df = build_carbon_intensity_forecast_from_elia(use_date=use_date)

        if forecast_df is None:
            return jsonify({"error": "Could not fetch forecast data"}), 500

        # Convert to JSON-friendly format
        forecast_data = []
        for idx in forecast_df.index:
            forecast_data.append(
                {
                    "datetime": idx.isoformat(),
                    "hour": idx.hour,
                    "total_load_mw": float(forecast_df.loc[idx, "total_load_mw"]),
                    "wind_mw": float(forecast_df.loc[idx, "wind_mw"]),
                    "solar_mw": float(forecast_df.loc[idx, "solar_mw"]),
                    "thermal_and_nuclear_mw": float(
                        forecast_df.loc[idx, "thermal_and_nuclear_mw"]
                    ),
                    "carbon_intensity": float(
                        forecast_df.loc[idx, "carbon_intensity_g_per_kWh"]
                    ),
                }
            )

        # Calculate summary statistics
        summary = {
            "min_carbon_intensity": float(
                forecast_df["carbon_intensity_g_per_kWh"].min()
            ),
            "max_carbon_intensity": float(
                forecast_df["carbon_intensity_g_per_kWh"].max()
            ),
            "avg_carbon_intensity": float(
                forecast_df["carbon_intensity_g_per_kWh"].mean()
            ),
            "date": forecast_df.index[0].strftime("%Y-%m-%d"),
            "total_hours": len(forecast_df),
        }

        return jsonify(
            {"success": True, "summary": summary, "hourly_data": forecast_data}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize-forecast", methods=["POST"])
def optimize_forecast():
    """Optimize load schedule based on carbon intensity forecast.

    This endpoint analyzes the carbon intensity forecast and finds the optimal time
    slot to run a load that minimizes carbon emissions. It compares the standard
    schedule against the optimal schedule and calculates potential savings.

    Request Body (JSON):
        power_kw (float): Load power in kW (required)
        duration_hours (int): Duration of the load in hours (required)
        standard_start_hour (int, optional): Typical start hour (0-23). Defaults to 6.
        date (str, optional): Date in YYYY-MM-DD format. If not provided, uses most
                             recent available data.

    Returns:
        Response: JSON object containing:
            - success (bool): Whether the optimization succeeded
            - date (str): The forecast date used
            - standard_profile (dict): Emissions data for the standard schedule
            - optimal_profile (dict): Emissions data for the optimal schedule
            - savings (dict): Emissions savings, percentage reduction, time shift,
                            and equivalent metrics (e.g., km of driving avoided)
            - hourly_data (list): Hour-by-hour forecast with windows marked

        Status Codes:
            200: Success
            400: Invalid request data or parameters
            500: Could not fetch forecast data or calculate optimization
    """
    try:
        # Get request data
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required parameters
        power_kw = data.get("power_kw")
        duration_hours = data.get("duration_hours")

        if power_kw is None or duration_hours is None:
            return jsonify({"error": "power_kw and duration_hours are required"}), 400

        # Convert power from kW to MW
        load_mw = float(power_kw) / 1000
        duration_hours = int(duration_hours)

        # Optional parameters
        standard_start_hour = data.get("standard_start_hour", 6)  # Default to 6am
        date_str = data.get("date")
        use_date = None

        if date_str:
            try:
                use_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Get carbon intensity forecast
        forecast_df = build_carbon_intensity_forecast_from_elia(use_date=use_date)

        if forecast_df is None:
            return jsonify({"error": "Could not fetch forecast data"}), 500

        # Calculate standard profile emissions
        standard_result = calculate_load_emissions(
            forecast_df, standard_start_hour, duration_hours, load_mw
        )

        # Find optimal time slot
        optimal_result, all_slots = find_optimal_timeslot(
            forecast_df, duration_hours, load_mw
        )

        if standard_result is None or optimal_result is None:
            return jsonify({"error": "Could not calculate optimization"}), 500

        # Calculate savings
        emissions_saved_kg = (
            standard_result["total_emissions_kg"] - optimal_result["total_emissions_kg"]
        )
        emissions_saved_pct = (
            emissions_saved_kg / standard_result["total_emissions_kg"]
        ) * 100
        time_shift_hours = (
            optimal_result["start_time"] - standard_result["start_time"]
        ).total_seconds() / 3600

        # Prepare hourly forecast data with highlighting
        hourly_data = []
        for idx in forecast_df.index:
            is_standard = (
                standard_result["start_time"] <= idx < standard_result["end_time"]
            )
            is_optimal = (
                optimal_result["start_time"] <= idx < optimal_result["end_time"]
            )

            hourly_data.append(
                {
                    "datetime": idx.isoformat(),
                    "hour": idx.hour,
                    "carbon_intensity": float(
                        forecast_df.loc[idx, "carbon_intensity_g_per_kWh"]
                    ),
                    "is_standard_window": is_standard,
                    "is_optimal_window": is_optimal,
                    "total_load_mw": float(forecast_df.loc[idx, "total_load_mw"]),
                    "wind_mw": float(forecast_df.loc[idx, "wind_mw"]),
                    "solar_mw": float(forecast_df.loc[idx, "solar_mw"]),
                    "thermal_and_nuclear_mw": float(
                        forecast_df.loc[idx, "thermal_and_nuclear_mw"]
                    ),
                }
            )

        # Prepare response
        response = {
            "success": True,
            "date": forecast_df.index[0].strftime("%Y-%m-%d"),
            "standard_profile": {
                "start_time": standard_result["start_time"].strftime("%H:%M"),
                "end_time": standard_result["end_time"].strftime("%H:%M"),
                "start_hour": standard_result["start_hour"],
                "duration_hours": duration_hours,
                "load_kw": power_kw,
                "energy_kwh": standard_result["energy_kwh"],
                "avg_carbon_intensity": standard_result[
                    "avg_carbon_intensity_g_per_kwh"
                ],
                "total_emissions_kg": standard_result["total_emissions_kg"],
            },
            "optimal_profile": {
                "start_time": optimal_result["start_time"].strftime("%H:%M"),
                "end_time": optimal_result["end_time"].strftime("%H:%M"),
                "start_hour": optimal_result["start_hour"],
                "duration_hours": duration_hours,
                "load_kw": power_kw,
                "energy_kwh": optimal_result["energy_kwh"],
                "avg_carbon_intensity": optimal_result[
                    "avg_carbon_intensity_g_per_kwh"
                ],
                "total_emissions_kg": optimal_result["total_emissions_kg"],
            },
            "savings": {
                "emissions_saved_kg": emissions_saved_kg,
                "emissions_saved_pct": emissions_saved_pct,
                "time_shift_hours": time_shift_hours,
                "km_equivalent": (emissions_saved_kg * 1000)
                / 120,  # Average car: 120g CO2/km
            },
            "hourly_data": hourly_data,
        }

        return jsonify(response)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for API monitoring.

    Simple endpoint to verify that the API server is running and responsive.
    Useful for load balancers, monitoring systems, and debugging.

    Returns:
        Response: JSON object containing:
            - status (str): Always "healthy" if server is running
            - timestamp (str): ISO 8601 formatted timestamp of the request

        Status Code:
            200: Server is healthy and responsive
    """
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    import os

    print("\n🌱 CarbonSaver API Server")
    print("=" * 70)

    # Determine if running in production (AWS) or development
    is_production = os.environ.get("AWS_EXECUTION_ENV") is not None

    if is_production:
        print("Running in PRODUCTION mode (AWS)")
        print("Server will be managed by WSGI server")
    else:
        print("Running in DEVELOPMENT mode")
        print("Server starting on http://localhost:5001")

    print("API Endpoints:")
    print("  GET  /api/forecast - Get carbon intensity forecast")
    print("  POST /api/optimize-forecast - Optimize load schedule")
    print("  GET  /api/health - Health check")
    print("=" * 70)
    print("\nPress Ctrl+C to stop the server\n")

    # Use use_reloader=False to avoid multiprocessing warnings
    # In production, this won't be called (WSGI server handles it)
    port = int(os.environ.get("PORT", 5001))
    debug = not is_production

    app.run(debug=debug, host="0.0.0.0", port=port, use_reloader=False)
