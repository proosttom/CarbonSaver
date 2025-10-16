# ENTSO-E API Setup

## Getting Your API Token

The CarbonSaver application uses the ENTSO-E Transparency Platform API to fetch real-time generation data. You need a free API token to use this service.

### Steps to Get Your Token:

1. **Visit ENTSO-E Transparency Platform**
   - Go to: https://transparency.entsoe.eu/

2. **Create an Account**
   - Click "Login" in the top right
   - Click "Register" if you don't have an account
   - Fill in your details and verify your email

3. **Generate API Token**
   - Log in to your account
   - Click on your username (top right)
   - Select "Web API Security Token"
   - Click "Generate a new token"
   - Copy your token (keep it secure!)

4. **Add Token to Your Environment**
   ```bash
   # Create a .env file in the project root
   cp .env.example .env
   
   # Edit .env and add your token
   ENTSOE_API_TOKEN=your_actual_token_here
   ```

5. **Restart the Application**
   ```bash
   python app.py
   ```

## Fallback Behavior

If no ENTSO-E token is provided, the application will automatically fall back to using the Elia Open Data API, which doesn't require authentication but may have different data formats.

## Data Coverage

- **ENTSO-E**: Pan-European data with standardized formats
- **Elia**: Belgium-specific data with detailed breakdowns

Both sources provide real-time generation data by fuel type for carbon intensity calculations.
