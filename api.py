from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

# CORS (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ------------------------
# Market data
# ------------------------
def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="2d")
    today = hist.iloc[-1]

    spot = round(today["Close"], 2)
    high = round(today["High"], 2)
    low = round(today["Low"], 2)
    atm = round(spot / 50) * 50

    return {
        "spot": spot,
        "high": high,
        "low": low,
        "atm": atm,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    }

# ------------------------
# Support / Resistance
# ------------------------
@app.get("/support-resistance")
def support_resistance():
    d = get_nifty_data()
    return {
        "spot": d["spot"],
        "support": d["low"],
        "resistance": d["high"],
        "logic": "Day Low = Support | Day High = Resistance",
        "validity": "Intraday",
        "disclaimer": "Educational purpose only"
    }

# ------------------------
# 9:30 Trade (GROQ AI)
# ------------------------
@app.get("/generate-report")
def generate_report():
    d = get_nifty_data()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = f"""
You are an expert Indian options trader.

NIFTY SPOT: {d['spot']}
ATM STRIKE: {d['atm']}
DATE: 07 Jan 2026
TIME: 9:30 AM – 3:00 PM
EXPIRY: 27 Jan 2026 (Monthly)
RISK: HIGH

Tasks:
1. Give probabilities (%) for:
   - Upside
   - Downside
   - Volatile
   (Total must be 100%)

2. Choose ONLY ONE:
   - BUY CALL
   - BUY PUT
   - BOTH
   - NO TRADE

3. Mention:
   - Strike
   - Approx premium (₹)
   - Expected return %
   - Risk %

End with **Actionable Summary**.
"""

    try:
        response = client.responses.create(
            model="llama-3.3-70b-versatile",
            input=prompt
        )

        return {
            "success": True,
            "spot": d["spot"],
            "atm": d["atm"],
            "generated_at": d["time"],
            "report": response.output_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Groq API failed: {str(e)}"
        )
