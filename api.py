from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from datetime import datetime
from openai import OpenAI  # pip install openai

app = FastAPI(title="Dhruv Stock Forecast API")

# Allow frontend to call API (important for Render + localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client (free tier)
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),  # Set this in Render Environment Variables
    base_url="https://api.groq.com/openai/v1"
)

def fetch_nifty_option_chain():
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            "Referer": "https://www.nseindia.com/option-chain",
            "Accept": "application/json",
        })
        # Get cookies first
        session.get("https://www.nseindia.com/", timeout=10)

        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        spot = round(data["records"]["underlyingValue"], 2)
        expiries = data["records"]["expiryDates"]

        # Prefer January 2026 monthly expiry, fallback to nearest
        target_expiry = expiries[0]
        for exp in expiries:
            if "Jan" in exp or "JAN" in exp and "26" in exp:
                target_expiry = exp
                break

        # Get options for target expiry
        options_data = [opt for opt in data["records"]["data"] if opt["expiryDate"] == target_expiry]

        # Find nearest ATM strike
        strikes = sorted({opt["strikePrice"] for opt in options_data})
        atm_strike = min(strikes, key=lambda x: abs(x - spot))

        # Get premiums
        call_premium = put_premium = "N/A"
        for opt in options_data:
            if opt["strikePrice"] == atm_strike:
                if "CE" in opt:
                    call_premium = opt["CE"].get("lastPrice", "N/A")
                if "PE" in opt:
                    put_premium = opt["PE"].get("lastPrice", "N/A")
                break

        return {
            "spot": spot,
            "atm_strike": atm_strike,
            "call_premium": call_premium,
            "put_premium": put_premium,
            "expiry": target_expiry,
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NSE data fetch failed: {str(e)}")

@app.get("/")
def home():
    return {"message": "Dhruv Stock Forecast API is live! 🚀"}

@app.get("/support-resistance")
def support_resistance():
    try:
        data = fetch_nifty_option_chain()
        return {
            "spot": data["spot"],
            "support": round(data["spot"] - 100, 2),  # Simple logic for demo
            "resistance": round(data["spot"] + 100, 2),
            "logic": "Simple range around spot (±100 points)",
            "validity": "Intraday",
            "disclaimer": "Educational purpose only"
        }
    except:
        return {"error": "Failed to fetch data"}

@app.get("/generate-report")
def generate_report():
    try:
        market_data = fetch_nifty_option_chain()
        spot = market_data["spot"]

        prompt = f"""
You are an expert financial analyst specializing in the Indian equity and derivatives markets, especially Nifty 50 options.

Current Nifty 50 spot level: {spot}
ATM Strike: {market_data['atm_strike']}
Call Premium ≈ ₹{market_data['call_premium']}
Put Premium ≈ ₹{market_data['put_premium']}
Expiry: {market_data['expiry']}

Today is 07 January 2026. Trading hours: 9:30 AM to 3:00 PM IST.

Using technical analysis (support/resistance, candlesticks, IV, Greeks), fundamental cues (FII/DII, global markets, news), and sentiment:

1. Give intraday probability estimates (%):
   - Chance Nifty closes higher than {spot}
   - Chance Nifty closes lower than {spot}
   - Chance of volatile move (big up or down)

2. Recommend the better high-risk intraday option buying strategy:
   - Buy near-ATM Calls only
   - Buy near-ATM Puts only
   Estimate expected return (%) and key risks.

3. End with a concise Actionable Summary:
   • Recommended strategy today
   • Strike to buy
   • Approx premium and success probability

Important: This is for educational purposes only. Not financial advice. Options trading carries high risk.
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Fast & smart on Groq
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        report = response.choices[0].message.content

        return {
            "success": True,
            "generated_at": market_data["timestamp"],
            "current_spot": spot,
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
