from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import os
from openai import OpenAI  # For Groq client (recommended)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

def fetch_nifty_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.nseindia.com/",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]
        for item in data:
            if item["symbol"] == "NIFTY 50":
                return item
        raise ValueError("NIFTY 50 not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NSE fetch failed: {str(e)}")

@app.get("/support-resistance")
def support_resistance():
    try:
        nifty = fetch_nifty_data()
        return {
            "spot": round(nifty["lastPrice"], 2),
            "support": round(nifty["dayLow"], 2),
            "resistance": round(nifty["dayHigh"], 2),
            "logic": "Day low as support, day high as resistance",
            "validity": "Today",
            "disclaimer": "Educational only"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-report")
def generate_report():
    try:
        nifty = fetch_nifty_data()
        spot = round(nifty["lastPrice"], 2)
        atm_strike = round(spot / 50) * 50

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        prompt = f"""Expert Nifty options analysis for today (07 Jan 2026).
Spot: {spot}
ATM Strike: {atm_strike}
Day High/Low: {nifty['dayHigh']}/{nifty['dayLow']}

Provide:
1. Intraday probabilities (up/down/volatile %)
2. Recommended high-risk strategy (buy Calls/Puts)
3. Expected return & risks
4. Actionable Summary (strategy, strike, premium approx, probability)"""

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        report = response.choices[0].message.content

        return {
            "success": True,
            "spot": spot,
            "atm_strike": atm_strike,
            "report": report,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        return {"error": f"Report failed: {str(e)}"}
