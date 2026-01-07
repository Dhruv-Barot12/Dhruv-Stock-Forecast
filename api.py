from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

def get_nifty():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="1d")
    today = hist.iloc[-1]
    spot = round(today["Close"], 2)
    return {
        "spot": spot,
        "high": round(today["High"], 2),
        "low": round(today["Low"], 2),
        "atm": round(spot / 50) * 50,
        "time": datetime.now().strftime("%d %b %Y %I:%M %p")
    }

@app.get("/support-resistance")
def support_resistance():
    d = get_nifty()
    return {
        "spot": d["spot"],
        "support": d["low"],
        "resistance": d["high"],
        "logic": "Day low = support, day high = resistance",
        "disclaimer": "Educational only"
    }

@app.get("/generate-report")
def generate_report():
    d = get_nifty()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"success": False, "error": "GROQ_API_KEY not set"}

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    prompt = f"""
Nifty Intraday Analysis
Spot: {d['spot']}
ATM: {d['atm']}
High: {d['high']}
Low: {d['low']}
Give strategy (Call/Put), probability, and risk.
"""

    r = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return {
        "success": True,
        "spot": d["spot"],
        "atm_strike": d["atm"],
        "report": r.choices[0].message.content,
        "generated_at": d["time"]
    }
