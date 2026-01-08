from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf
from datetime import datetime
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

# ---------- FRONTEND ----------
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ---------- MARKET DATA ----------
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

# ---------- SUPPORT / RESISTANCE ----------
@app.get("/support-resistance")
def support_resistance():
    d = get_nifty_data()
    return {
        "spot": d["spot"],
        "support": d["low"],
        "resistance": d["high"],
        "logic": "Day Low = Support | Day High = Resistance",
        "validity": "Intraday only",
        "disclaimer": "Educational purpose only"
    }

# ---------- 9:30 TRADE (GROQ AI) ----------
@app.get("/generate-report")
def generate_report():
    d = get_nifty_data()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

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

Give probabilities (%):
1. Upside
2. Downside
3. Volatile

Rules:
• Recommend ONLY ONE: BUY CALL / BUY PUT / BOTH / NO TRADE
• If probabilities unclear → NO TRADE
• Mention strike, approx premium, expected return %, risk %

End with **Actionable Summary**.
"""

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )

        report = response.choices[0].message.content.strip()

        return {
            "success": True,
            "spot": d["spot"],
            "atm": d["atm"],
            "generated_at": d["time"],
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API failed: {str(e)}")
