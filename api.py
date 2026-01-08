from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

# CORS (required)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ------------------------
# MARKET DATA
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
# SUPPORT / RESISTANCE
# ------------------------
@app.get("/support-resistance")
def support_resistance():
    data = get_nifty_data()
    return {
        "spot": data["spot"],
        "support": data["low"],
        "resistance": data["high"],
        "logic": "Day Low = Support | Day High = Resistance",
        "validity": "Intraday",
        "disclaimer": "Educational use only"
    }

# ------------------------
# 9:30 TRADE AI
# ------------------------
@app.get("/nine-thirty-trade")
def nine_thirty_trade():
    try:
        data = get_nifty_data()

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        prompt = f"""
You are an expert Indian stock market analyst.

Nifty 50 Spot: {data['spot']}
ATM Strike: {data['atm']}
High: {data['high']} | Low: {data['low']}
Date: 07 Jan 2026
Expiry: 27 Jan 2026 (Monthly)
Risk: HIGH
Trading Time: 9:30 AM – 3:00 PM

TASK:
1. Give probability (%) of:
   - Upside
   - Downside
   - Volatile (big move either side)

2. Choose ONLY ONE:
   - Buy ATM Call
   - Buy ATM Put
   - Buy BOTH
   - NO TRADE

3. Mention expected return %, risks, and confidence.

End with **Actionable Summary**.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ ACTIVE MODEL
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=700
        )

        return {
            "success": True,
            "spot": data["spot"],
            "atm": data["atm"],
            "generated_at": data["time"],
            "report": response.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service failed: {str(e)}")
