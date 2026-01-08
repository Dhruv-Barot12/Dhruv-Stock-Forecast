from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime, time
import pytz
import os
from openai import OpenAI

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STATIC ----------------
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ---------------- TIMEZONE ----------------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def is_valid_prompt_time():
    now = ist_now().time()
    return time(9, 20) <= now <= time(9, 28)

# ---------------- MARKET DATA ----------------
def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="2d")
    today = hist.iloc[-1]

    spot = round(today["Close"], 2)
    high = round(today["High"], 2)
    low = round(today["Low"], 2)
    atm = round(spot / 50) * 50

    return spot, high, low, atm

# ---------------- SUPPORT / RESISTANCE ----------------
@app.get("/support-resistance")
def support_resistance():
    spot, high, low, _ = get_nifty_data()
    return {
        "spot": spot,
        "support": low,
        "resistance": high
    }

# ---------------- 9:30 TRADE ----------------
@app.get("/generate-report")
def generate_report():

    now = ist_now()

    weekly_expiry = "09 Jan 2026"
    monthly_expiry = "27 Jan 2026"

    # ❌ TIME BLOCK
    if not is_valid_prompt_time():
        return {
            "no_trade": True,
            "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
            "weekly_expiry": weekly_expiry,
            "monthly_expiry": monthly_expiry
        }

    spot, high, low, atm = get_nifty_data()

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = f"""
You are an expert NIFTY 50 options trader.

Spot: {spot}
ATM: {atm}
Day High: {high}
Day Low: {low}

Rules:
- Always ONE strategy only (CALL or PUT or NO TRADE)
- High-risk intraday view
- Give probabilities for Upside / Downside / Volatile
- Give strike, expected return %, risk %
- Short actionable summary
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=500
    )

    return {
        "spot": spot,
        "atm": atm,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry,
        "monthly_expiry": monthly_expiry,
        "report": response.choices[0].message.content
    }
