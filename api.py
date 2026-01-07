from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
from datetime import datetime
from openai import OpenAI

app = FastAPI(title="Dhruv Stock Forecast")

# CORS - Allow your frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the Frontend folder (so index.html loads at root URL)
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# Root route - serves your index.html
@app.get("/")
def read_root():
    return FileResponse("Frontend/index.html")

# Groq API client (free)
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),  # You will set this in Render
    base_url="https://api.groq.com/openai/v1"
)

def fetch_nifty_option_chain():
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            "Referer": "https://www.nseindia.com/option-chain",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        })
        # Get cookies
        session.get("https://www.nseindia.com/", timeout=10)

        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        spot = round(data["records"]["underlyingValue"], 2)
        expiries = data["records"]["expiryDates"]

        # Try to find January 2026 expiry, fallback to nearest
        target_expiry = expiries[0]
        for exp in expiries:
            if "Jan" in exp or "JAN" in exp and "26" in exp:
                target_expiry = exp
                break

        options_data = [opt for opt in data["records"]["data"] if opt.get("expiryDate") == target_expiry]

        strikes = sorted({opt["strikePrice"] for opt in options_data if "strikePrice" in opt})
        atm_strike = min(strikes, key=lambda x: abs(x - spot)) if strikes else spot

        call_premium = put_premium = "N/A"
        for opt in options_data:
            if opt.get("strikePrice") == atm_strike:
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch NSE data: {str(e)}")

@app.get("/support-resistance")
def support_resistance():
    try:
        data = fetch_nifty_option_chain()
        # Simple logic for now (you can improve later)
        return {
            "spot": data["spot"],
            "support": round(data["spot"] - 150, 2),
            "resistance": round(data["spot"] + 150, 2),
            "logic": "Approximate intraday range (±150 points from spot)",
            "validity": "Intraday",
            "disclaimer": "For educational purposes only"
        }
    except Exception as e:
        return {"error": "Could not fetch data", "details": str(e)}

@app.get("/generate-report")
def generate_report():
    try:
        market_data = fetch_nifty_option_chain()
        spot = market_data["spot"]

        prompt = f"""
You are an expert Indian stock market analyst specializing in Nifty 50 and options trading.

Current Date: 07 January 2026
Current Nifty Spot: {spot}
Near ATM Strike: {market_data['atm_strike']}
Call Premium: ≈ ₹{market_data['call_premium']}
Put Premium: ≈ ₹{market_data['put_premium']}
Target Expiry: {market_data['expiry']}

Trading session: 9:30 AM to 3:00 PM IST
Strategy: High-risk intraday option buying

Using technical analysis, support/resistance, implied volatility, global cues, FII/DII data, news sentiment:

1. Estimate intraday probabilities (%):
   - Nifty closes higher than current spot
   - Nifty closes lower than current spot
   - High volatility move expected

2. Recommend which is better today for intraday profit:
   - Buy near-ATM CALLS only
   - Buy near-ATM PUTS only

   For the better one, estimate:
   - Expected return potential (%)
   - Key risks (time decay, volatility crush, news events)

3. End with a clear Actionable Summary:
   • Recommended action today (Buy Calls / Buy Puts / Avoid)
   • Suggested strike
   • Approx premium to pay
   • Success probability

Disclaimer: This is for educational purposes only. Not financial advice. Options trading is high risk.
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        report = response.choices[0].message.content.strip()

        return {
            "success": True,
            "generated_at": market_data["timestamp"],
            "current_spot": spot,
            "atm_strike": market_data["atm_strike"],
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI report failed: {str(e)}")
