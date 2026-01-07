from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ---------------- DATA ---------------- #

def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="1d")

    if hist.empty:
        raise HTTPException(status_code=500, detail="No Nifty data")

    row = hist.iloc[-1]
    spot = round(row["Close"], 2)

    return {
        "spot": spot,
        "day_high": round(row["High"], 2),
        "day_low": round(row["Low"], 2),
        "atm_strike": round(spot / 50) * 50,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    }

# ---------------- ROUTES ---------------- #

@app.get("/support-resistance")
def support_resistance():
    data = get_nifty_data()
    return {
        "spot": data["spot"],
        "support": data["day_low"],
        "resistance": data["day_high"],
        "logic": "Day low as support, day high as resistance",
        "validity": "Intraday",
        "disclaimer": "Educational only",
    }

@app.get("/generate-report")
def generate_report():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

    data = get_nifty_data()

    prompt = f"""
Nifty 50 Intraday Analysis

Spot: {data['spot']}
ATM Strike: {data['atm_strike']}
Day High: {data['day_high']}
Day Low: {data['day_low']}

Give:
1. Direction probability (%)
2. Call or Put recommendation
3. Risk & reward
4. Short actionable summary
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "max_tokens": 500,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Groq API failed: {response.text}",
        )

    report = response.json()["choices"][0]["message"]["content"]

    return {
        "success": True,
        "spot": data["spot"],
        "atm_strike": data["atm_strike"],
        "report": report,
        "generated_at": data["timestamp"],
    }
