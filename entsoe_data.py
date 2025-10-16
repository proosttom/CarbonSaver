import requests
import pandas as pd
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

# ENTSO-E API Configuration
ENTSOE_API_BASE = "https://web-api.tp.entsoe.eu/api"

# Belgium EIC code (Energy Identification Code)
BELGIUM_EIC = "10YBE----------2"

# Emission Factors (gCO₂eq / kWh)
EMISSION_FACTORS = {
    "Solar": 15,
    "Wind Onshore": 11.5,
    "Wind Offshore": 11.5,
    "Nuclear": 5,
    "Fossil Gas": 490,
    "Fossil Hard coal": 820,
    "Hydro Water Reservoir": 24,
    "Hydro Run-of-river": 24,
    "Biomass": 230,
    "Waste": 200,
    "Other": 200,
}


def fetch_realtime_production(security_token=None):
    """Fetches real-time power generation data aggregated by fuel type from ENTSO-E.

    This function retrieves actual generation per production type from ENTSO-E
    Transparency Platform API for Belgium.

    Args:
        security_token (str, optional): ENTSO-E API security token. If not provided,
                                       will try to read from environment variable.

    Returns:
        dict: A dictionary containing current production data with keys:
            - timestamp: ISO format timestamp of the latest data
            - production: dict with fuel types as keys and MW values
            - total_mw: Total generation in MW
            - carbon_intensity_g_per_kwh: Current carbon intensity in g/kWh
            Returns None if the fetch fails.
    """
    import os

    # Get security token from parameter or environment
    token = security_token or os.environ.get("ENTSOE_API_TOKEN")

    if not token:
        print(
            "⚠️ ENTSO-E API token not provided. Set ENTSOE_API_TOKEN environment variable."
        )
        print("   Get your token at: https://transparency.entsoe.eu/")
        return None

    # Define time range - use UTC time and round to full hours
    end_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=24)

    # Format times in ENTSO-E format (YYYYMMDDHHmm) - ENTSO-E requires UTC
    period_start = start_time.strftime("%Y%m%d%H%M")
    period_end = end_time.strftime("%Y%m%d%H%M")

    # API parameters for Actual Generation per Type (A75)
    params = {
        "securityToken": token,
        "documentType": "A75",  # Actual generation per type
        "processType": "A16",  # Realised
        "in_Domain": BELGIUM_EIC,
        "periodStart": period_start,
        "periodEnd": period_end,
    }

    try:
        print(
            f"🔄 Fetching ENTSO-E data for Belgium ({period_start} to {period_end})..."
        )
        response = requests.get(ENTSOE_API_BASE, params=params, timeout=30)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        # Define namespace
        ns = {"ns": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"}

        # Extract all TimeSeries (each represents a production type)
        production = {}
        latest_timestamp = None

        for timeseries in root.findall(".//ns:TimeSeries", ns):
            # Get production type
            psr_type = timeseries.find(".//ns:MktPSRType/ns:psrType", ns)
            if psr_type is None:
                continue

            fuel_type = psr_type.text

            # Get the most recent Point (data point)
            points = timeseries.findall(".//ns:Point", ns)
            if not points:
                continue

            # Get last point
            last_point = points[-1]
            quantity = last_point.find("ns:quantity", ns)

            if quantity is not None:
                power_mw = float(quantity.text)

                # Map fuel type names
                fuel_name = map_entsoe_fuel_type(fuel_type)

                if fuel_name in production:
                    production[fuel_name] += power_mw
                else:
                    production[fuel_name] = power_mw

        # Get timestamp from Period
        period = root.find(".//ns:Period", ns)
        if period is not None:
            timeInterval = period.find("ns:timeInterval", ns)
            if timeInterval is not None:
                end_elem = timeInterval.find("ns:end", ns)
                if end_elem is not None:
                    latest_timestamp = end_elem.text

        if not latest_timestamp:
            latest_timestamp = end_time.isoformat()

        # Calculate totals and carbon intensity
        total_power = sum(production.values())
        total_emissions = sum(
            power * EMISSION_FACTORS.get(fuel_type, 200) * 1000
            for fuel_type, power in production.items()
        )

        carbon_intensity = (
            total_emissions / (total_power * 1000) if total_power > 0 else 0
        )

        result = {
            "timestamp": latest_timestamp,
            "production": production,
            "total_mw": total_power,
            "carbon_intensity_g_per_kwh": carbon_intensity,
        }

        print(f"✅ Fetched ENTSO-E production data: {total_power:.0f} MW total")
        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching ENTSO-E data: {e}")
        return None
    except ET.ParseError as e:
        print(f"❌ Error parsing ENTSO-E XML response: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def map_entsoe_fuel_type(entsoe_code):
    """Map ENTSO-E production type codes to friendly names.

    Args:
        entsoe_code (str): ENTSO-E production type code

    Returns:
        str: Friendly fuel type name
    """
    mapping = {
        "B01": "Biomass",
        "B02": "Fossil Brown coal/Lignite",
        "B03": "Fossil Coal-derived gas",
        "B04": "Fossil Gas",
        "B05": "Fossil Hard coal",
        "B06": "Fossil Oil",
        "B09": "Geothermal",
        "B10": "Hydro Pumped Storage",
        "B11": "Hydro Run-of-river",
        "B12": "Hydro Water Reservoir",
        "B13": "Marine",
        "B14": "Nuclear",
        "B15": "Other renewable",
        "B16": "Solar",
        "B17": "Waste",
        "B18": "Wind Offshore",
        "B19": "Wind Onshore",
        "B20": "Other",
    }

    return mapping.get(entsoe_code, "Other")


# --- Real-time Production Data Function ---
def fetch_realtime_production_backup():
    """Fetches real-time power generation data aggregated by fuel type from Entsoe.

    This is a backup function that falls back to Elia API if ENTSO-E fails.
    """
    from elia_forecast import fetch_realtime_production as fetch_elia

    return fetch_elia()
