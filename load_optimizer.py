import pandas as pd
from datetime import datetime, time, timedelta
from elia_forecast import build_carbon_intensity_forecast_from_elia


def calculate_load_emissions(carbon_forecast, start_hour, duration_hours, load_mw):
    """
    Calculate total emissions for a load profile starting at a specific hour.

    Args:
        carbon_forecast: DataFrame with carbon intensity (g/kWh) indexed by datetime
        start_hour: Hour of day to start (0-23)
        duration_hours: Duration of the load in hours
        load_mw: Load in MW (constant for simplicity)

    Returns:
        dict with total emissions, average carbon intensity, and time window
    """
    # Filter forecast to only include times matching the start hour
    forecast_df = carbon_forecast.copy()
    forecast_df["hour"] = forecast_df.index.hour

    # Find all slots that match the start hour
    possible_starts = forecast_df[forecast_df["hour"] == start_hour].index

    if len(possible_starts) == 0:
        return None

    # Use the first matching slot (should only be one day in the forecast)
    start_time = possible_starts[0]
    end_time = start_time + timedelta(hours=duration_hours)

    # Get carbon intensity for the time window
    window_data = forecast_df[
        (forecast_df.index >= start_time) & (forecast_df.index < end_time)
    ]

    if len(window_data) == 0:
        return None

    # Calculate emissions
    # Load (MW) * Hours * 1000 (to kW) * Carbon Intensity (g/kWh) / 1000 (to kg)
    energy_kwh = load_mw * duration_hours * 1000
    avg_carbon_intensity = window_data["carbon_intensity_g_per_kWh"].mean()
    total_emissions_kg = (energy_kwh * avg_carbon_intensity) / 1000

    return {
        "start_time": start_time,
        "end_time": end_time,
        "start_hour": start_hour,
        "duration_hours": duration_hours,
        "load_mw": load_mw,
        "energy_kwh": energy_kwh,
        "avg_carbon_intensity_g_per_kwh": avg_carbon_intensity,
        "total_emissions_kg": total_emissions_kg,
        "window_data": window_data,
    }


def find_optimal_timeslot(carbon_forecast, duration_hours, load_mw):
    """
    Find the optimal time slot with minimum carbon emissions.

    Args:
        carbon_forecast: DataFrame with carbon intensity indexed by datetime
        duration_hours: Duration of the load in hours
        load_mw: Load in MW

    Returns:
        dict with optimal start time and emissions data
    """
    best_slot = None
    best_emissions = float("inf")
    all_slots = []

    forecast_df = carbon_forecast.copy()

    # Try all possible start times
    for start_time in forecast_df.index:
        end_time = start_time + timedelta(hours=duration_hours)

        # Check if we have enough data for this window
        window_data = forecast_df[
            (forecast_df.index >= start_time) & (forecast_df.index < end_time)
        ]

        # Need at least the duration in hours worth of data
        if len(window_data) < duration_hours:
            continue

        # Calculate emissions for this slot
        energy_kwh = load_mw * duration_hours * 1000
        avg_carbon_intensity = window_data["carbon_intensity_g_per_kWh"].mean()
        total_emissions_kg = (energy_kwh * avg_carbon_intensity) / 1000

        slot_info = {
            "start_time": start_time,
            "end_time": end_time,
            "start_hour": start_time.hour,
            "duration_hours": duration_hours,
            "load_mw": load_mw,
            "energy_kwh": energy_kwh,
            "avg_carbon_intensity_g_per_kwh": avg_carbon_intensity,
            "total_emissions_kg": total_emissions_kg,
        }

        all_slots.append(slot_info)

        if total_emissions_kg < best_emissions:
            best_emissions = total_emissions_kg
            best_slot = slot_info

    return best_slot, all_slots


def compare_load_profiles(
    standard_start_hour, duration_hours, load_mw, forecast_date=None
):
    """
    Compare a standard load profile with the optimal load profile.

    Args:
        standard_start_hour: Standard start hour (e.g., 7 for 7am)
        duration_hours: Duration of the load in hours
        load_mw: Load in MW
        forecast_date: Optional specific date to use

    Returns:
        dict with comparison results
    """
    print("=" * 70)
    print("LOAD PROFILE OPTIMIZER - Carbon Emission Comparison")
    print("=" * 70)

    # Get carbon intensity forecast
    print("\nFetching carbon intensity forecast...")
    carbon_forecast = build_carbon_intensity_forecast_from_elia(use_date=forecast_date)

    if carbon_forecast is None:
        print("ERROR: Could not fetch carbon forecast data")
        return None

    print(f"✓ Forecast data retrieved for {carbon_forecast.index[0].date()}")

    # Calculate emissions for standard profile
    print("\n" + "-" * 70)
    print("STANDARD LOAD PROFILE")
    print("-" * 70)
    standard_result = calculate_load_emissions(
        carbon_forecast, standard_start_hour, duration_hours, load_mw
    )

    if standard_result is None:
        print(f"ERROR: Could not calculate emissions for standard profile")
        return None

    print(
        f"Start Time:              {standard_result['start_time'].strftime('%Y-%m-%d %H:%M')}"
    )
    print(
        f"End Time:                {standard_result['end_time'].strftime('%Y-%m-%d %H:%M')}"
    )
    print(f"Duration:                {duration_hours} hours")
    print(f"Load:                    {load_mw} MW")
    print(f"Total Energy:            {standard_result['energy_kwh']:,.0f} kWh")
    print(
        f"Avg Carbon Intensity:    {standard_result['avg_carbon_intensity_g_per_kwh']:.2f} gCO₂/kWh"
    )
    print(
        f"Total Emissions:         {standard_result['total_emissions_kg']:.2f} kg CO₂"
    )

    # Find optimal time slot
    print("\n" + "-" * 70)
    print("OPTIMAL LOAD PROFILE (Searching for minimum emissions...)")
    print("-" * 70)
    optimal_result, all_slots = find_optimal_timeslot(
        carbon_forecast, duration_hours, load_mw
    )

    if optimal_result is None:
        print("ERROR: Could not find optimal time slot")
        return None

    print(
        f"Start Time:              {optimal_result['start_time'].strftime('%Y-%m-%d %H:%M')}"
    )
    print(
        f"End Time:                {optimal_result['end_time'].strftime('%Y-%m-%d %H:%M')}"
    )
    print(f"Duration:                {duration_hours} hours")
    print(f"Load:                    {load_mw} MW")
    print(f"Total Energy:            {optimal_result['energy_kwh']:,.0f} kWh")
    print(
        f"Avg Carbon Intensity:    {optimal_result['avg_carbon_intensity_g_per_kwh']:.2f} gCO₂/kWh"
    )
    print(f"Total Emissions:         {optimal_result['total_emissions_kg']:.2f} kg CO₂")

    # Calculate savings
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    emissions_saved_kg = (
        standard_result["total_emissions_kg"] - optimal_result["total_emissions_kg"]
    )
    emissions_saved_pct = (
        emissions_saved_kg / standard_result["total_emissions_kg"]
    ) * 100
    time_shift_hours = (
        optimal_result["start_time"] - standard_result["start_time"]
    ).total_seconds() / 3600

    print(
        f"Emissions Saved:         {emissions_saved_kg:.2f} kg CO₂ ({emissions_saved_pct:.1f}%)"
    )
    print(f"Time Shift:              {time_shift_hours:+.0f} hours")

    if emissions_saved_kg > 0:
        print(
            f"\n✓ By shifting the load from {standard_result['start_time'].strftime('%H:%M')} to "
            f"{optimal_result['start_time'].strftime('%H:%M')}, you can save {emissions_saved_kg:.2f} kg CO₂!"
        )
    else:
        print(f"\n✓ The standard profile is already optimal or near-optimal!")

    # Show hourly breakdown
    print("\n" + "-" * 70)
    print("HOURLY CARBON INTENSITY PROFILE")
    print("-" * 70)
    print(f"{'Hour':<8} {'Carbon Intensity (g/kWh)':<30} {'Status':<20}")
    print("-" * 70)

    for idx in carbon_forecast.index:
        hour_str = idx.strftime("%H:%M")
        intensity = carbon_forecast.loc[idx, "carbon_intensity_g_per_kWh"]
        bar_length = int(intensity / 10)
        bar = "█" * bar_length

        # Mark standard and optimal windows
        status = ""
        if standard_result["start_time"] <= idx < standard_result["end_time"]:
            status = "← STANDARD"
        if optimal_result["start_time"] <= idx < optimal_result["end_time"]:
            status += " ← OPTIMAL" if status else "← OPTIMAL"

        print(f"{hour_str:<8} {bar:<30} {intensity:>6.1f} {status}")

    return {
        "standard": standard_result,
        "optimal": optimal_result,
        "emissions_saved_kg": emissions_saved_kg,
        "emissions_saved_pct": emissions_saved_pct,
        "time_shift_hours": time_shift_hours,
        "all_slots": all_slots,
        "carbon_forecast": carbon_forecast,
    }


# --- To run this script directly for testing ---
if __name__ == "__main__":
    print("\n")
    print("🌱 CarbonSaver - Load Profile Optimizer")
    print("\n")

    # Example: 1 MWh load for 4 hours starting at 7am (standard profile)
    standard_start_hour = 7  # 7am
    duration_hours = 4
    load_mw = 0.25  # 0.25 MW for 4 hours = 1 MWh

    results = compare_load_profiles(
        standard_start_hour=standard_start_hour,
        duration_hours=duration_hours,
        load_mw=load_mw,
    )

    if results:
        print("\n" + "=" * 70)
        print("Analysis complete!")
        print("=" * 70)
