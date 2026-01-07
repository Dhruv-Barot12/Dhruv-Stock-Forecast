from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the Frontend folder
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

def fetch_nifty_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()["data"]
        for item in data:
            if item["symbol"] == "NIFTY 50":
                return item
        raise ValueError("NIFTY 50 not found in data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NSE data fetch failed: {str(e)}")

@app.get("/support-resistance")
def support_resistance():
    try:
        nifty = fetch_nifty_data()
        return {
            "spot": round(nifty["lastPrice"], 2),
            "support": round(nifty["dayLow"], 2),
            "resistance": round(nifty["dayHigh"], 2),
            "logic": "Day low as support, day high as resistance",
            "validity": "Intraday",
            "disclaimer": "For educational purposes only"
        }
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}

@app.get("/generate-report")
def generate_report():
    try:
        nifty = fetch_nifty_data()
        spot = round(nifty["lastPrice"], 2)
        atm_strike = round(spot / 50) * 50

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY not configured"}

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        prompt = f"""You are an expert Nifty 50 options analyst. Current date: 07 January 2026.

Current Nifty Spot: {spot}
Near ATM Strike: {atm_strike}
Day High: {nifty['dayHigh']} | Day Low: {nifty['dayLow']}

Provide a short intraday report with:
1. Probability estimates (%): close higher, close lower, volatile move
2. Recommended high-risk strategy: Buy near-ATM Calls or Puts
3. Expected return potential and major risks
4. Actionable Summary: strategy, strike, approx premium, success probability

Disclaimer: Educational purpose only. Not financial advice."""

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
        return {"error": f"Report generation failed: {str(e)}"}
