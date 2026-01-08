from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, time, timedelta
import pytz
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# ------------------ UTILITIES ------------------

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    data = ticker.history(period="1d", interval="1m")
    last = data.iloc[-1]
    spot = round(last["Close"], 2)
    atm = round(spot / 50) * 50
    return spot, atm

def get_weekly_expiry(today):
    days_ahead = (3 - today.weekday()) % 7  # Thursday
    expiry = today + timedelta(days=days_ahead)
    return expiry.strftime("%d %b %Y")

def get_monthly_expiry(today):
    month_end = today.replace(day=28) + timedelta(days=4)
    last_day = month_end - timedelta(days=month_end.day)
    while last_day.weekday() != 3:
        last_day -= timedelta(days=1)
    return last_day.strftime("%d %b %Y")

# ------------------ API ------------------

@app.get("/support-resistance")
def support_resistance():
    spot, atm = get_nifty_data()
    return {
        "spot": spot,
        "support": atm - 100,
        "resistance": atm + 100
    }


@app.get("/trade-930")
def trade_930():
    now = ist_now()
    start = time(9, 20)
    end = time(9, 28)

    today = now.date()

    weekly_expiry = get_weekly_expiry(today)
    monthly_expiry = get_monthly_expiry(today)

    # Time restriction
    if not (start <= now.time() <= end):
        return {
            "status": "NO TRADE",
            "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
            "weekly_expiry": weekly_expiry,
            "monthly_expiry": monthly_expiry,
            "reason": "Outside execution window"
        }

    spot, atm = get_nifty_data()

    return {
        "status": "BUY CALL",
        "spot": spot,
        "atm": atm,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry,
        "monthly_expiry": monthly_expiry,
        "probabilities": {
            "upside": 60,
            "downside": 20,
            "volatile": 20
        },
        "trade": {
            "strike": atm,
            "estimated_premium": 420,
            "expected_return_pct": 15,
            "risk_pct": 80
        },
        "summary": "Buy NIFTY ATM CALL for intraday momentum with high risk."
    }
