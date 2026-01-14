from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import yfinance as yf
from datetime import datetime
import pytz

app = FastAPI()

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

@app.get("/")
def root():
    return {"status": "API running"}

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

        # ---- BASE PROBABILITIES ----
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

        # ---- ACTIONABLE LOGIC ----
        if volatility >= 40:
            action = (
                "High volatility expected. Trade only with strict risk control. "
                "ATM straddle possible for experienced traders."
            )
        elif upside >= downside + 5:
            action = (
                "Upside bias detected. Prefer buying near-ATM CALL options "
                "with strict stop-loss."
            )
        elif downside >= upside + 5:
            action = (
                "Downside bias detected. Prefer buying near-ATM PUT options "
                "with strict stop-loss."
            )
        else:
            action = "No clear edge today. Avoid aggressive option buying."

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
