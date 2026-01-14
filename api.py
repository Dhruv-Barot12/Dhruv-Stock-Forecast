from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime, timezone, timedelta

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- UTIL ----------
def ist_now():
    return datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=5, minutes=30))
    )

# ---------- FRONTEND ----------
@app.get("/")
def home():
    # IMPORTANT: index.html is inside Frontend folder
    return FileResponse("Frontend/index.html")

# ---------- 9:30 PROBABILITY API ----------
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

        # ---- Base probabilities (neutral day) ----
        upside = 40
        downside = 40
        flat = 20
        volatility = 30

        # ---- Adjust probabilities using gap logic ----
        if gap_pct > 0.4:
            upside += 5
            flat -= 5
        elif gap_pct < -0.4:
            downside += 5
            flat -= 5

        if abs(gap_pct) > 1:
            volatility = 45

        return {
            "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
            "reference_level": spot,
            "upside": f"{upside}%",
            "downside": f"{downside}%",
            "flat": f"{flat}%",
            "volatility": f"{volatility}%",
            "generated_at": ist_now().strftime("%d %B %Y, %I:%M %p IST")
        }

    except Exception as e:
        return {"error": str(e)}
