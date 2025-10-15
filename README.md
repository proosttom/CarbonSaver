# CarbonSaver - Energy Flexibility Market POC

A proof-of-concept project demonstrating energy flexibility market link to carbon intensity. Using real data from the Elia Open Data Platform.

## Overview

This project fetches real-time grid data from Belgium's transmission system operator (Elia) and calculates carbon intensity forecasts to help optimize energy consumption during low-carbon periods.

## Features

- Fetches day-ahead forecasts from Elia's Open Data API:
  - Total load forecast (ods001)
  - Wind power generation (ods032)
  - Solar power generation (ods087)
- Calculates carbon intensity (gCO₂eq/kWh) based on generation mix
- Resamples 15-minute data to hourly forecasts
- No API key required - uses Elia's open data platform

## Setup

### Prerequisites

- Python 3.7+
- Virtual environment (venv)

### Installation

1. Clone or download this repository

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

Run the Flask web application for a full interactive experience:

```bash
python app.py
```

Then open your browser to: **http://localhost:5001**

The web interface provides:
- Interactive form for load profile configuration
- Real-time carbon intensity forecasting
- Visual comparison of standard vs optimal schedules
- Interactive charts with Chart.js
- Emissions savings calculations with real-world equivalents

### Interactive Load Optimizer (CLI)

Run the interactive CLI for a guided terminal experience:

```bash
python cli.py
```

The CLI will ask you for:
- Start hour of your standard schedule
- Duration in hours
- Total energy consumption in MWh

Then it will show you the optimal schedule and emissions savings.

### Basic Carbon Forecast

Run the forecast script:

```bash
python elia_forecast.py
```

This will automatically find the most recent date with complete data available and display the carbon intensity for each hour. 

**Note**: Due to publishing schedules, day-ahead forecasts may not always be available for tomorrow. The script will automatically search backwards from yesterday to find the most recent complete dataset (for POC demonstration purposes).

You can also specify a specific date:

```python
from datetime import date
from elia_forecast import build_carbon_intensity_forecast_from_elia

# Get forecast for a specific date
forecast = build_carbon_intensity_forecast_from_elia(use_date=date(2025, 10, 13))

# The forecast DataFrame contains:
# - total_load_mw: Total load in MW
# - wind_mw: Wind generation in MW
# - solar_mw: Solar generation in MW
# - thermal_and_nuclear_mw: Other generation in MW
# - total_emissions_gCO2eq_per_h: Total emissions per hour
# - carbon_intensity_g_per_kWh: Carbon intensity in g/kWh

# Example: Get the hour with minimum carbon intensity
min_hour = forecast['carbon_intensity_g_per_kWh'].idxmin()
print(f"Lowest carbon intensity at: {min_hour}")
```

### Interactive Load Optimizer (Recommended)

Run the interactive CLI for a guided experience:

```bash
python cli.py
```

The CLI will ask you for:
- Start hour of your standard schedule
- Duration in hours
- Total energy consumption in MWh

Then it will show you the optimal schedule and emissions savings.

## API Endpoints Used

- **Load Forecast**: `https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods001/records`
- **Wind Forecast**: `https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods032/records`
- **Solar Forecast**: `https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods087/records`

## Emission Factors

The following emission factors are used (gCO₂eq/kWh):
- Solar: 15
- Wind: 11.5 (average of onshore/offshore)
- Thermal & Nuclear: 199 (weighted mix of ~60% nuclear @ 5g/kWh, 40% gas @ 490g/kWh)

## API Endpoints

The Flask application provides the following REST API endpoints:

### `POST /api/optimize-forecast`
Optimize load schedule based on carbon intensity forecast.

**Request Body:**
```json
{
  "power_kw": 250,
  "duration_hours": 4,
  "standard_start_hour": 7
}
```

**Response:**
```json
{
  "success": true,
  "date": "2025-10-13",
  "standard_profile": { ... },
  "optimal_profile": { ... },
  "savings": {
    "emissions_saved_kg": 38.40,
    "emissions_saved_pct": 26.5,
    "time_shift_hours": 3,
    "km_equivalent": 320
  },
  "hourly_data": [ ... ]
}
```

### `GET /api/forecast`
Get carbon intensity forecast without optimization.

### `GET /api/health`
Health check endpoint.

## Technologies Used

### Backend
- Python 3.7+
- Flask (REST API)
- pandas (data manipulation)
- requests (API calls)

### Frontend
- HTML5/CSS3
- JavaScript (ES6+)
- Chart.js (data visualization)

### Data Sources

## Load Profile Optimization

### Programmatic Usage

The project includes a load optimizer that compares a standard load profile with the optimal time slot for minimum carbon emissions:

```bash
python load_optimizer.py
```

### Example Output

```
STANDARD LOAD PROFILE: 7am-11am → 145.03 kg CO₂
OPTIMAL LOAD PROFILE:  10am-2pm → 106.63 kg CO₂
SAVINGS: 38.40 kg CO₂ (26.5% reduction)
```

### Custom Load Profiles

You can customize the load profile in the script:

```python
from load_optimizer import compare_load_profiles

results = compare_load_profiles(
    standard_start_hour=7,    # 7am start time
    duration_hours=4,         # 4 hours duration
    load_mw=0.25             # 0.25 MW load (= 1 MWh total)
)
```

The optimizer:
- Calculates total emissions for your standard load profile
- Searches all possible time slots to find the optimal window
- Shows emissions savings and recommended time shift
- Displays an hourly carbon intensity chart

## Project Structure

```
CarbonSaver/
├── app.py                # Flask web application
├── elia_forecast.py      # Carbon intensity forecast engine
├── load_optimizer.py     # Load profile optimizer (programmatic)
├── cli.py               # Interactive CLI interface
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/              # Web application assets
│   ├── index.html       # Main HTML page
│   ├── style.css        # Styles
│   └── script.js        # Frontend JavaScript
└── .venv/              # Virtual environment (gitignored)
```

## Integration

To integrate this into a Flask application:

```python
from elia_forecast import build_carbon_intensity_forecast_from_elia

# In your Flask endpoint
@app.route('/optimize-forecast')
def optimize_forecast():
    forecast = build_carbon_intensity_forecast_from_elia()
    if forecast is not None:
        # Process and return the forecast
        return jsonify(forecast.to_dict())
    else:
        return jsonify({"error": "Failed to fetch forecast"}), 500
```

## Data Sources

- [Elia Open Data Platform](https://opendata.elia.be/)
- [API Documentation](https://opendata.elia.be/api/)

## License

This project uses data from Elia under the Elia Open Data Licence.

## Notes

- Data is updated every 15 minutes
- Day-ahead forecasts are typically published at 6 PM the day before
- The script automatically aggregates regional data for wind and solar
- Handles pagination for datasets with more than 100 records
