from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf
from datetime import datetime
import pytz
import os

app = FastAPI()

# ---------------- TIMEZONE ----------------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

# ---------------- FRONTEND SERVING ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------- API STATUS ----------------
@app.get("/api-status")
def api_status():
    return {"status": "API running"}

# ---------------- 9:30 PROBABILITY API ----------------
@app.get("/probability-930")
def probability_930():
    try:
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period="6d", interval="1d")

        if data.empty or len(data) < 2:
            return {"error": "Market data unavailable"}

        today = data.iloc[-1]
        prev = data.iloc[-2]

        spot = round(float(today["Close"]), 2)
        prev_close = float(prev["Close"])
        gap_pct = (spot - prev_close) / prev_close * 100

        # Base probabilities
        upside = 40
        downside = 40
        flat = 20
        volatility = 30

        if gap_pct > 0.4:
            upside += 5
            flat -= 5
        elif gap_pct < -0.4:
            downside += 5
            flat -= 5

        if abs(gap_pct) > 1:
            volatility = 45

        # Actionable logic
        if volatility >= 40:
            action = (
                "High volatility expected. High-risk traders may consider "
                "ATM straddle or directional option buying with strict stop-loss."
            )
        elif upside >= downside + 5:
            action = (
                "Upside bias. Prefer buying near-ATM CALL options. "
                "Momentum continuation expected."
            )
        elif downside >= upside + 5:
            action = (
                "Downside bias. Prefer buying near-ATM PUT options. "
                "Trend favors selling pressure."
            )
        else:
            action = (
                "No clear edge. Avoid aggressive option buying today."
            )

        return {
            "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
            "reference_level": spot,
            "upside": upside,
            "downside": downside,
            "flat": flat,
            "volatility": volatility,
            "actionable_summary": action,
            "generated_at": ist_now().strftime("%d %B %Y, %I:%M %p IST")
        }

    except Exception as e:
        return {"error": str(e)}
