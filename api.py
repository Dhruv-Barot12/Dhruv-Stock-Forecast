from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import pytz
import os
from openai import OpenAI

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- STATIC ----------
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ---------- IST TIME ----------
def ist_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d %b %Y, %I:%M %p IST")

# ---------- MARKET DATA ----------
def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="2d")
    today = hist.iloc[-1]

    spot = round(float(today["Close"]), 2)
    high = round(float(today["High"]), 2)
    low = round(float(today["Low"]), 2)
    atm = round(spot / 50) * 50

    return {
        "spot": spot,
        "high": high,
        "low": low,
        "atm": atm,
        "time": ist_time()
    }

# ---------- SUPPORT / RESISTANCE ----------
@app.get("/support-resistance")
def support_resistance():
    data = get_nifty_data()
    return {
        "spot": data["spot"],
        "support": data["low"],
        "resistance": data["high"],
        "logic": "Day Low = Support | Day High = Resistance",
        "validity": "Intraday",
        "generated": data["time"]
    }

# ---------- 9:30 TRADE ----------
@app.get("/nine-thirty-trade")
def nine_thirty_trade():
    data = get_nifty_data()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set"}

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = f"""
You are an expert Indian options trader.

NIFTY Spot: {data['spot']}
ATM Strike: {data['atm']}
Date: 07 Jan 2026
Trading Time: 9:30 AM – 3:00 PM IST
Expiry: 27 Jan 2026 (Monthly)
Risk Profile: HIGH

Rules:
- Always suggest ONLY ONE strategy (CALL OR PUT OR NO TRADE)
- NEVER suggest BUY PUT unless clearly dominant
- Give probabilities totaling 100%
- If probabilities are unclear → NO TRADE

Return format strictly:

Probabilities:
Upside: %
Downside: %
Volatile: %

Final Decision: BUY CALL / BUY PUT / NO TRADE

If Trade:
Strike:
Estimated Premium (₹):
Expected Return %:
Risk %:

Actionable Summary (2 lines)
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=600
    )

    report = response.choices[0].message.content.strip()

    return {
        "spot": data["spot"],
        "atm": data["atm"],
        "generated": data["time"],
        "report": report
    }
