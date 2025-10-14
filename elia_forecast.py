import requests
import pandas as pd
from datetime import datetime, timedelta

# Emission Factors (gCO₂eq / kWh) - simplified for the POC
EMISSION_FACTORS = {
    "solar": 15,
    "wind": 11.5,  # Average of onshore/offshore
    # This is our inferred "other" category. In Belgium, this is a mix of
    # nuclear (~5 g/kWh) and gas (~490 g/kWh). We'll use a weighted average
    # based on a typical mix. Let's assume ~60% nuclear, 40% gas for this part.
    "thermal_and_nuclear": (5 * 0.6) + (490 * 0.4),  # Approx. 199 g/kWh
}


# --- Helper Function to Fetch Data from Elia ---
def fetch_elia_data(dataset, start_date, end_date):
    """
    Fetches data from the Elia Open Data API for a given dataset and time range.
    """
    url = (
        f"https://opendata.elia.be/api/explore/v2.1/catalog/datasets/{dataset}/records"
    )
    params = {
        "where": f"datetime>='{start_date.isoformat()}' and datetime<'{end_date.isoformat()}'",
        "limit": 100,
        "offset": 0,
    }

    all_records = []
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
            data = response.json()

            if "results" not in data or len(data["results"]) == 0:
                break

            all_records.extend(data["results"])

            # Check if we have all records
            if len(all_records) >= data.get("total_count", 0):
                break

            params["offset"] += params["limit"]

        return pd.DataFrame(all_records)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {dataset}: {e}")
        return None


# --- Main Logic Function ---
def build_carbon_intensity_forecast_from_elia(use_date=None):
    """
    Builds a day-ahead carbon intensity forecast using Elia's open data.

    Args:
        use_date: Optional date to use for the forecast. If None, will try to find
                 the most recent date with available data (for POC purposes).
    """
    # 1. Define the time window
    if use_date:
        target_date = use_date
        next_date = target_date + timedelta(days=1)
        print(
            f"Building forecast for specified date: {target_date.strftime('%Y-%m-%d')}"
        )
    else:
        # For POC: Try to get the most recent date with available wind data
        # Start from yesterday and work backwards
        print("Searching for most recent date with complete data...")
        for days_offset in range(-1, -8, -1):  # Try last 7 days
            target_date = datetime.now().date() + timedelta(days=days_offset)
            next_date = target_date + timedelta(days=1)

            print(f"  Checking {target_date.strftime('%Y-%m-%d')}...", end=" ")

            # Quick check if wind data exists for this date
            wind_df_test = fetch_elia_data("ods032", target_date, next_date)

            # Check if we have wind data (most restrictive)
            if wind_df_test is not None and not wind_df_test.empty:
                print(f"✓ Found complete data!")
                break
            else:
                print("✗")
        else:
            print("ERROR: Could not find any data for the last 7 days")
            return None

    # Fetch all datasets with the confirmed date
    print(f"\nFetching complete dataset for {target_date.strftime('%Y-%m-%d')}...")
    load_df = fetch_elia_data("ods001", target_date, next_date)
    wind_df = fetch_elia_data("ods032", target_date, next_date)
    solar_df = fetch_elia_data("ods087", target_date, next_date)

    # 2. Validate datasets

    if load_df is None or wind_df is None or solar_df is None:
        print("Failed to fetch one or more datasets. Aborting.")
        return None

    # Check if dataframes have data
    if load_df.empty:
        print("ERROR: Load dataset returned no data")
        return None
    if wind_df.empty:
        print("ERROR: Wind dataset returned no data")
        return None
    if solar_df.empty:
        print("ERROR: Solar dataset returned no data")
        return None

    # 3. Process and combine the data
    # Convert 'datetime' column to actual datetime objects and set as index
    load_df["datetime"] = pd.to_datetime(load_df["datetime"])
    wind_df["datetime"] = pd.to_datetime(wind_df["datetime"])
    solar_df["datetime"] = pd.to_datetime(solar_df["datetime"])

    load_df.set_index("datetime", inplace=True)
    wind_df.set_index("datetime", inplace=True)
    solar_df.set_index("datetime", inplace=True)

    # For wind and solar, we need to aggregate by region (sum across all regions)
    wind_df_agg = wind_df.groupby("datetime")["dayaheadforecast"].sum()
    solar_df_agg = solar_df.groupby("datetime")["dayaheadforecast"].sum()

    # Resample from 15-min to hourly averages and select relevant columns
    hourly_load = (
        load_df["dayaheadforecast"].resample("h").mean().rename("total_load_mw")
    )
    hourly_wind = wind_df_agg.resample("h").mean().rename("wind_mw")
    hourly_solar = solar_df_agg.resample("h").mean().rename("solar_mw")

    # Combine into a single DataFrame
    forecast_df = pd.concat([hourly_load, hourly_wind, hourly_solar], axis=1).fillna(0)

    # 4. Infer the "Thermal and Nuclear" generation
    forecast_df["thermal_and_nuclear_mw"] = (
        forecast_df["total_load_mw"] - forecast_df["wind_mw"] - forecast_df["solar_mw"]
    )
    # Ensure it's not negative (can happen with forecast inaccuracies)
    forecast_df["thermal_and_nuclear_mw"] = forecast_df["thermal_and_nuclear_mw"].clip(
        lower=0
    )

    # 5. Calculate Total Emissions
    forecast_df["total_emissions_gCO2eq_per_h"] = (
        forecast_df["solar_mw"] * EMISSION_FACTORS["solar"] * 1000  # Convert MW to kW
        + forecast_df["wind_mw"] * EMISSION_FACTORS["wind"] * 1000
        + forecast_df["thermal_and_nuclear_mw"]
        * EMISSION_FACTORS["thermal_and_nuclear"]
        * 1000
    )

    # 6. Calculate Carbon Intensity (g/kWh)
    # Avoid division by zero if total load is forecasted to be zero
    forecast_df["carbon_intensity_g_per_kWh"] = forecast_df[
        "total_emissions_gCO2eq_per_h"
    ] / (forecast_df["total_load_mw"] * 1000)
    forecast_df.fillna(0, inplace=True)

    print("Forecast built successfully!")
    return forecast_df


# --- To run this script directly for testing ---
if __name__ == "__main__":
    # This block will only run when you execute `python elia_forecast.py`
    final_forecast = build_carbon_intensity_forecast_from_elia()

    if final_forecast is not None:
        print("\n--- Day-Ahead Carbon Intensity Forecast ---")
        print(final_forecast)

        print("\n--- Summary Statistics ---")
        print(
            f"Min Carbon Intensity: {final_forecast['carbon_intensity_g_per_kWh'].min():.2f} gCO₂/kWh"
        )
        print(
            f"Max Carbon Intensity: {final_forecast['carbon_intensity_g_per_kWh'].max():.2f} gCO₂/kWh"
        )
        print(
            f"Avg Carbon Intensity: {final_forecast['carbon_intensity_g_per_kWh'].mean():.2f} gCO₂/kWh"
        )
        print(f"\nTotal Load: {final_forecast['total_load_mw'].sum():.2f} MWh")
        print(f"Total Wind: {final_forecast['wind_mw'].sum():.2f} MWh")
        print(f"Total Solar: {final_forecast['solar_mw'].sum():.2f} MWh")
        print(
            f"Total Thermal/Nuclear: {final_forecast['thermal_and_nuclear_mw'].sum():.2f} MWh"
        )
