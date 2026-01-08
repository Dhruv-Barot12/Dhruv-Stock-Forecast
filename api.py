from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# -----------------------
# MARKET DATA
# -----------------------
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
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    }

# -----------------------
# SUPPORT & RESISTANCE
# -----------------------
@app.get("/support-resistance")
def support_resistance():
    d = get_nifty_data()
    return {
        "spot": d["spot"],
        "support": d["low"],
        "resistance": d["high"],
        "validity": "Intraday",
        "logic": "Day Low = Support, Day High = Resistance"
    }

# -----------------------
# 9:30 AI TRADE
# -----------------------
@app.get("/trade-930")
def trade_930():
    try:
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

Rules (STRICT):
- Choose ONLY ONE: BUY CALL OR BUY PUT OR NO TRADE
- DO NOT mention the other strategies
- Provide clear probabilities totaling 100%

Market:
NIFTY Spot: {d['spot']}
ATM Strike: {d['atm']}
Support: {d['low']}
Resistance: {d['high']}
Date: 07 Jan 2026
Time Window: 9:30 AM – 3:00 PM
Expiry: 27 Jan 2026 (Monthly)
Risk: HIGH

Output FORMAT (strict):

Probabilities:
Upside: XX%
Downside: XX%
Volatile: XX%

Final Decision: BUY CALL / BUY PUT / NO TRADE

If trade:
Strike:
Estimated Premium (₹):
Expected Return %:
Risk %:

Actionable Summary (2 lines max)
"""

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )

        report = res.choices[0].message.content.strip()

        return {
            "spot": d["spot"],
            "atm": d["atm"],
            "generated": d["time"],
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
