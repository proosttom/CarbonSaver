# CarbonSaver POC - Project Summary

## Overview
A proof-of-concept demonstrating energy flexibility market optimization using real-time grid data from Belgium's transmission system operator (Elia).

## Key Features Implemented

### 1. Real-Time Carbon Intensity Forecasting (`elia_forecast.py`)
- ✅ Fetches day-ahead forecasts from Elia Open Data API (no API key required)
- ✅ Combines load, wind, and solar generation data
- ✅ Calculates carbon intensity (gCO₂eq/kWh) based on generation mix
- ✅ Handles regional aggregation for wind and solar
- ✅ Resamples 15-minute data to hourly forecasts
- ✅ Automatic fallback to find most recent available data

### 2. Load Profile Optimizer (`load_optimizer.py`)
- ✅ Compares standard load profile with optimal timing
- ✅ Searches all possible time slots for minimum emissions
- ✅ Calculates emissions savings in kg CO₂ and percentage
- ✅ Visual hourly carbon intensity chart
- ✅ Shows time shift recommendations

### 3. Interactive CLI Interface (`cli.py`)
- ✅ User-friendly guided interface
- ✅ Input validation
- ✅ Clear recommendations with relatable comparisons
- ✅ Professional output formatting

## Technical Highlights

### Data Sources
- **Elia Open Data Platform** (Belgium TSO)
  - ods001: Load forecast
  - ods032: Wind generation forecast
  - ods087: Solar generation forecast

### Emission Factors Used
- Solar: 15 gCO₂eq/kWh
- Wind: 11.5 gCO₂eq/kWh
- Thermal & Nuclear: 199 gCO₂eq/kWh (weighted mix)

### Technologies
- Python 3.7+
- pandas: Data manipulation
- requests: API calls
- datetime: Time handling

## Real Results Example

Using October 13, 2025 data:

**Standard Profile** (7am-11am):
- Energy: 1,000 kWh
- Carbon Intensity: 145.03 gCO₂/kWh
- Total Emissions: 145.03 kg CO₂

**Optimal Profile** (10am-2pm):
- Energy: 1,000 kWh
- Carbon Intensity: 106.63 gCO₂/kWh
- Total Emissions: 106.63 kg CO₂

**Savings**: 38.40 kg CO₂ (26.5% reduction) by shifting 3 hours later

This is equivalent to:
- ~320 km of avoided driving
- Taking a typical car off the road for 2.7 days
- One person's daily carbon footprint

## Business Value Demonstration

This POC demonstrates:

1. **Data Integration Skills**: Successfully integrating multiple real-time data sources from external APIs
2. **Algorithm Development**: Creating optimization algorithms for practical energy problems
3. **User Experience**: Building intuitive interfaces for technical solutions
4. **Domain Knowledge**: Understanding energy markets, carbon accounting, and grid operations
5. **Professional Code Quality**: Clean, documented, maintainable code structure

## Scalability Considerations

For production deployment, this POC could be extended with:
- Database storage for historical analysis
- Real-time monitoring and alerts
- Multi-region support
- Integration with smart building/industrial systems
- Machine learning for demand prediction
- Cost optimization (combining carbon and electricity prices)
- API endpoints for third-party integration

## Use Cases

This technology is applicable to:
- **Industrial facilities**: Schedule energy-intensive processes
- **Data centers**: Optimize batch job timing
- **EV charging**: Smart charging during low-carbon periods
- **Building management**: HVAC and thermal storage optimization
- **Energy communities**: Coordinate flexible loads

## Demonstration of Professional Skills

### Software Engineering
- Modular design with clear separation of concerns
- Error handling and edge case management
- User input validation
- Comprehensive documentation

### Data Engineering
- API integration and pagination handling
- Data cleaning and transformation
- Time series resampling
- Regional data aggregation

### Domain Expertise
- Understanding of grid operations
- Carbon accounting methodology
- Load profile analysis
- Optimization algorithms

## Next Steps for Production

1. Add unit tests and integration tests
2. Implement caching for API responses
3. Add logging and monitoring
4. Create REST API for external integration
5. Build web dashboard for visualization
6. Add support for multiple regions/countries
7. Integrate electricity pricing data
8. Add forecasting accuracy metrics

## Contact & Discussion

This POC is ready for:
- Technical deep-dive discussions
- Architecture review
- Feature extension brainstorming
- Integration planning

---

**Note**: This is a proof-of-concept for demonstration purposes. Production deployment would require additional error handling, testing, monitoring, and compliance considerations.
