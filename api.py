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

# ---------------- DATA ---------------- #

def get_nifty_data():
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- SUPPORT / RESISTANCE ---------------- #

@app.get("/support-resistance")
def support_resistance():
    data = get_nifty_data()
    return {
        "spot": data["spot"],
        "support": data["low"],
        "resistance": data["high"],
        "logic": "Day Low = Support | Day High = Resistance",
        "validity": "Intraday",
        "disclaimer": "Educational purpose only"
    }

# ---------------- 9:30 TRADE ---------------- #

@app.get("/nine-thirty-trade")
def nine_thirty_trade():
    data = get_nifty_data()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = f"""
You are an expert Indian Nifty 50 options trader.

STRICT RULES:
- Choose ONLY ONE strategy:
  BUY CALL OR BUY PUT OR BUY BOTH OR NO TRADE
- If probabilities are unclear → NO TRADE
- NEVER list rejected strategies
- NEVER explain hedging alternatives

Market Data:
Spot: {data['spot']}
ATM: {data['atm']}
High/Low: {data['high']} / {data['low']}
Expiry: 27 Jan 2026 (Monthly)
Risk: HIGH
Time window: 9:30 AM – 3:00 PM

Tasks:
1. Probability (%):
   - Upside
   - Downside
   - Volatile
   (Total = 100%)

2. Pick ONE strategy only.

3. Provide details ONLY for selected strategy:
   - Strike
   - Approx premium ₹
   - Expected return %
   - Risk %

4. End with Actionable Summary:
   - Final trade
   - Confidence %

No disclaimers inside analysis.
"""

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=700
        )

        return {
            "spot": data["spot"],
            "atm": data["atm"],
            "generated": data["time"],
            "report": response.choices[0].message.content.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API failed: {str(e)}")
