from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timezone, timedelta
import yfinance as yf
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("Frontend/index.html")

def ist_now():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))

def round_to_50(x):
    return int(round(x / 50.0) * 50)

@app.get("/trade")
def trade():
    # --- Fetch live-ish data from Yahoo Finance ---
    ticker = yf.Ticker("^NSEI")
    hist = ticker.history(period="2d", interval="1d")

    if hist.empty or len(hist) < 2:
        return {"error": "Market data unavailable"}

    prev = hist.iloc[-2]
    today = hist.iloc[-1]

    spot = float(today["Close"])
    open_px = float(today["Open"])
    high = float(today["High"])
    low = float(today["Low"])
    prev_close = float(prev["Close"])

    gap = spot - prev_close
    day_range = high - low
    atm = round_to_50(spot)

    # --- Simple, explainable rule engine ---
    bias = "Neutral"
    final_decision = "NO TRADE"

    if gap < -60 and spot < open_px:
        bias = "Bearish"
        final_decision = "BUY PUT"
    elif gap > 60 and spot > open_px:
        bias = "Bullish"
        final_decision = "BUY CALL"
    elif day_range < 120:
        bias = "Range-bound"
        final_decision = "NO TRADE"

    # --- Expiry text (static but correct calendar-wise) ---
    weekly_expiry = "Next Thursday (Weekly)"
    monthly_expiry = "27 January 2026 (Monthly)"

    # --- Strategy text (both scenarios shown) ---
    text = f"""
Market Snapshot
• NIFTY Spot: {spot:.2f}
• Previous Close: {prev_close:.2f}
• Gap: {gap:+.2f}
• Day Range (H-L): {day_range:.0f}
• Bias: {bias}

1- Buying Put options only (near ATM)
Recommended strike: {atm} PE or {atm-100} PE
Expected move: 180–350 points (if downside accelerates)
Volatility expectation: Moderate to High
Use when: Weak price below open, sustained selling pressure

2- Buying Call options only (near ATM)
Recommended strike: {atm} CE or {atm+100} CE
Expected move: 120–280 points (requires strength)
Volatility expectation: Moderate
Use when: Strong reclaim above open with follow-through

Actionable Summary – {ist_now().strftime('%d %B %Y')}
• Final Decision: {final_decision}
• Reason: {bias} conditions based on gap, open relation, and range
• Trading Window: 9:30 AM – 3:00 PM IST
• Expiry: Weekly ({weekly_expiry}) | Monthly ({monthly_expiry})
"""

    return {
        "spot": round(spot, 2),
        "atm": atm,
        "generated_at": ist_now().strftime("%d %B %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry,
        "monthly_expiry": monthly_expiry,
        "output": text.strip()
    }
