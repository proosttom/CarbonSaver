# CarbonSaver Quick Start Guide

## ⚡ Get Real-Time Production Data Working

The Live Grid Production dashboard requires an ENTSO-E API token. Here's how to set it up in 5 minutes:

### Step 1: Get Your Free API Token

1. Go to **https://transparency.entsoe.eu/**
2. Click **"Login"** (top right) → **"Register"**
3. Fill in your details and verify your email
4. Log in and click your username → **"Web API Security Token"**
5. Click **"Generate a new token"**
6. **Copy the token** (you'll need it in the next step)

### Step 2: Add Token to Your Environment

```bash
# Create a .env file in the project root (if it doesn't exist)
cd /Users/proost/Coding/CarbonSaver

# Add your token to the .env file
echo "ENTSOE_API_TOKEN=your_actual_token_here" >> .env
```

**Or manually edit `.env` file:**
```bash
ENTSOE_API_TOKEN=your_actual_token_here
PORT=5001
FLASK_ENV=development
```

### Step 3: Install python-dotenv (if not already installed)

```bash
/Users/proost/Coding/CarbonSaver/.venv/bin/pip install python-dotenv
```

### Step 4: Restart the Server

```bash
/Users/proost/Coding/CarbonSaver/.venv/bin/python app.py
```

### Step 5: Open the App

Visit **http://localhost:5001** in your browser

You should now see real-time data in the "🔌 Live Grid Production" dashboard!

---

## 🔧 Troubleshooting

**Problem:** "API token required" message
- **Solution:** Make sure you created the `.env` file with your token
- **Check:** Token should be on a single line with no quotes or spaces

**Problem:** "Unable to fetch real-time data"
- **Solution:** Check that your token is valid at https://transparency.entsoe.eu/
- **Try:** Regenerate the token if it's expired

**Problem:** Server shows "Tip: There are .env files present. Install python-dotenv"
- **Solution:** Run: `/Users/proost/Coding/CarbonSaver/.venv/bin/pip install python-dotenv`

---

## ℹ️ More Information

- Full setup guide: See `ENTSOE_SETUP.md`
- API Documentation: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
