from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
import requests

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------- FRONTEND ---------------
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ------------- DATA --------------------

def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="1d")

    if hist.empty:
        raise HTTPException(status_code=500, detail="No Nifty data available")

    row = hist.iloc[-1]
    spot = round(row["Close"], 2)

    return {
        "spot": spot,
        "high": round(row["High"], 2),
        "low": round(row["Low"], 2),
        "atm": round(spot / 50) * 50,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    }

# -------- SUPPORT / RESISTANCE ---------

@app.get("/support-resistance")
def support_resistance():
    d = get_nifty_data()
    return {
        "spot": d["spot"],
        "support": d["low"],
        "resistance": d["high"],
        "logic": "Day low used as support and day high as resistance",
        "validity": "Intraday",
        "disclaimer": "Educational purposes only",
    }

# -------- AI INTRADAY REPORT ------------

@app.get("/generate-report")
def generate_report():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    d = get_nifty_data()

    prompt = f"""
NIFTY 50 INTRADAY ANALYSIS

Spot Price: {d['spot']}
ATM Strike: {d['atm']}
Day High: {d['high']}
Day Low: {d['low']}

Provide:
1. Direction probability (Bullish/Bearish/Sideways)
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
            "model": "llama-3.1-8b-instant",   # ✅ CURRENT SUPPORTED MODEL
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
        "spot": d["spot"],
        "atm_strike": d["atm"],
        "report": report,
        "generated_at": d["time"],
    }
