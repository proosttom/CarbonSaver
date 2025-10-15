# CarbonSaver Web Application - User Guide

## 🌱 Welcome to CarbonSaver!

CarbonSaver is a web-based tool that helps you optimize your energy consumption schedule to minimize carbon emissions. By analyzing real-time grid data from Belgium's transmission system operator (Elia), it identifies the optimal time windows for running energy-intensive loads.

## Getting Started

### 1. Start the Application

```bash
cd /Users/username/Coding/CarbonSaver
python app.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:5001**

## Using the Application

### Step 1: Configure Your Load Profile

Fill in the form with your load characteristics:

- **Power (kW)**: The power consumption of your load
  - Example: 250 kW for an industrial process
  
- **Duration (hours)**: How long the load will run
  - Example: 4 hours for a batch process

- **Standard Start Hour**: Your typical start time (0-23 format)
  - Example: 7 for 7:00 AM

### Step 2: Get Optimization Results

Click the **"Get Forecast & Optimize"** button.

The application will:
1. Fetch the latest carbon intensity forecast from Elia
2. Calculate emissions for your standard schedule
3. Find the optimal time slot with minimum emissions
4. Display comprehensive results

## Understanding the Results

### Date Information
Shows which date the forecast is for (note: may be historical data for demonstration if tomorrow's data isn't available yet)

### Standard Schedule Card (Yellow/Orange)
- Your current/typical schedule
- Shows start/end times, energy consumption
- Carbon intensity and total emissions

### Optimal Schedule Card (Green)
- The recommended optimal schedule
- Same energy consumption
- Lower carbon intensity and emissions

### Savings Banner (Green)
Key metrics displayed:
- **Emissions Saved**: Total CO₂ reduction in kg
- **Reduction %**: Percentage improvement
- **Time Shift**: Hours difference from standard schedule
- **Equivalent**: Comparison to km of driving avoided

### Carbon Intensity Chart
Interactive bar chart showing:
- **Blue bars**: Normal hours
- **Yellow bars**: Your standard schedule window
- **Green bars**: Optimal schedule window
- Height represents carbon intensity (gCO₂/kWh)

**Hover over bars** to see detailed information:
- Exact carbon intensity value
- Total grid load
- Wind and solar generation

## Real-World Example

**Input:**
- Power: 250 kW
- Duration: 4 hours
- Standard Start: 7:00 AM

**Results:**
- Standard Schedule: 7:00-11:00 → 145.03 kg CO₂
- Optimal Schedule: 10:00-14:00 → 106.63 kg CO₂
- **Savings: 38.40 kg CO₂ (26.5% reduction)**
- Equivalent to avoiding 320 km of driving!

## Why Does This Work?

Carbon intensity varies throughout the day based on:
- **Solar Power**: Peaks during midday (10 AM - 2 PM)
- **Wind Power**: Variable but often higher overnight
- **Thermal/Nuclear**: Fills the gap, has higher emissions

By shifting loads to periods of high renewable generation (especially solar midday), you consume the same energy but with significantly lower carbon footprint.

## Tips for Best Results

1. **Flexible Loads**: Works best with loads that have scheduling flexibility
2. **Longer Duration**: Longer loads may benefit more from optimization
3. **Check Daily**: Carbon forecasts change based on weather and grid conditions
4. **Plan Ahead**: Use forecasts to schedule next-day operations

## Use Cases

### Industrial Applications
- Batch manufacturing processes
- Heating/cooling cycles
- Water treatment and pumping
- Compressed air generation

### Commercial Buildings
- HVAC pre-conditioning
- Ice/thermal storage charging
- Laundry and kitchen equipment
- EV fleet charging

### Data Centers
- Batch job processing
- Backup operations
- Data migration tasks
- Non-critical workloads

## Technical Details

### Data Source
- **Elia Open Data Platform**: Belgium's TSO real-time grid data
- No API key required
- Updates every 15 minutes
- Includes day-ahead forecasts

### Calculation Method
1. Fetches load, wind, and solar forecasts
2. Calculates remaining generation (thermal/nuclear)
3. Applies emission factors:
   - Solar: 15 gCO₂/kWh
   - Wind: 11.5 gCO₂/kWh
   - Thermal/Nuclear: 199 gCO₂/kWh (weighted mix)
4. Optimizes by testing all possible time windows

### Accuracy
- Based on day-ahead forecasts (actual values may vary)
- Suitable for planning and decision support
- Production use should include additional validation

## API Integration

For programmatic access, use the REST API:

```bash
# Get forecast only
curl http://localhost:5001/api/forecast

# Optimize schedule
curl -X POST http://localhost:5001/api/optimize-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "power_kw": 250,
    "duration_hours": 4,
    "standard_start_hour": 7
  }'
```

## Troubleshooting

### "Could not fetch forecast data"
- Check internet connection
- Elia API may be temporarily unavailable
- Try again in a few minutes

### "Wind dataset returned no data"
- Tomorrow's forecast may not be published yet
- Application will automatically use most recent available data

### Chart not displaying
- Ensure Chart.js library loads (check browser console)
- Try refreshing the page
- Check browser compatibility (Chrome, Firefox, Safari, Edge)

## Privacy & Data

- All processing happens locally on your machine
- No personal data is collected or stored
- API calls go directly to Elia Open Data (public data)
- No cookies or tracking

## Support & Feedback

This is a proof-of-concept demonstration project. For:
- Feature requests
- Bug reports
- Integration questions
- Commercial applications

Contact the developer or check the project README.

---