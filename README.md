# CarbonSaver

A web application that helps optimize energy consumption timing based on real-time carbon intensity data from Belgium's electricity grid.

## Features

- **Live Grid Production**: Real-time electricity generation by source (wind, solar, nuclear, gas, etc.) from ENTSO-E
- **Carbon Intensity Forecasting**: Day-ahead forecasts from Elia's transmission data
- **Load Optimization**: Find the best time windows to minimize carbon emissions
- **Interactive Dashboard**: Visual charts and real-time data updates
- **Emissions Calculator**: Compare standard vs. optimized schedules with savings in kg CO₂ and km driven equivalents

## Quick Start

1. **Clone and setup**:
```bash
git clone <repository-url>
cd CarbonSaver
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. **Configure environment** (create `.env` file):
```bash
ENTSOE_API_TOKEN=your_token_here
```
Get your free token at: https://transparency.entsoe.eu/

3. **Run the application**:
```bash
python app.py
```

4. **Open browser**: http://localhost:5001

See [QUICKSTART.md](QUICKSTART.md) and [ENTSOE_SETUP.md](ENTSOE_SETUP.md) for detailed setup instructions.

## API Endpoints

### `GET /api/realtime-production`
Real-time electricity generation by fuel type from ENTSO-E.

**Response**:
```json
{
  "success": true,
  "timestamp": "2025-10-16T14:30:00Z",
  "production": {
    "Wind Onshore": 1250.0,
    "Solar": 890.5,
    "Nuclear": 3800.0,
    "Fossil Gas": 1200.0,
    ...
  },
  "total_mw": 7500.0,
  "carbon_intensity_g_per_kwh": 120.5
}
```

### `POST /api/optimize-forecast`
Optimize load schedule based on carbon intensity forecast.

**Request**:
```json
{
  "power_kw": 250,
  "duration_hours": 4,
  "standard_start_hour": 7
}
```

**Response**:
```json
{
  "success": true,
  "date": "2025-10-16",
  "savings": {
    "emissions_saved_kg": 38.40,
    "emissions_saved_pct": 26.5,
    "time_shift_hours": 3
  },
  "hourly_data": [...]
}
```

### `GET /api/forecast`
Get carbon intensity forecast without optimization.

### `GET /api/health`
Health check endpoint.

## Emission Factors

Carbon intensity values (gCO₂eq/kWh):
- **Nuclear**: 5 | **Wind**: 11.5 | **Solar**: 15 | **Hydro**: 24
- **Biomass**: 230 | **Waste**: 200 | **Gas**: 490

Hover over production types in the UI to see emission factors.

## Project Structure

```
CarbonSaver/
├── app.py                  # Flask API server
├── elia_forecast.py        # Elia data fetching & carbon forecasting
├── entsoe_data.py          # ENTSO-E real-time production data
├── load_optimizer.py       # Load optimization algorithms
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
├── static/
│   ├── index.html         # Web UI
│   ├── style.css          # Styles
│   └── script.js          # Frontend logic
└── .env                   # Environment variables (not in git)
```

## Technologies

- **Backend**: Python, Flask, pandas, requests
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Data Sources**: [Elia Open Data](https://opendata.elia.be/), [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)

## CLI Usage

Interactive command-line interface:
```bash
python cli.py
```

Direct optimization:
```python
from load_optimizer import compare_load_profiles

results = compare_load_profiles(
    standard_start_hour=7,
    duration_hours=4,
    load_mw=0.25
)
```

## Deployment

- **AWS Elastic Beanstalk**: See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
- **Production ready**: Includes Gunicorn, background data prefetching, and error handling

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Step-by-step setup guide
- [ENTSOE_SETUP.md](ENTSOE_SETUP.md) - ENTSO-E API configuration
- [USER_GUIDE.md](USER_GUIDE.md) - Application usage guide
- [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - Production deployment

## License

This project uses data from Elia Open Data Platform and ENTSO-E Transparency Platform.
