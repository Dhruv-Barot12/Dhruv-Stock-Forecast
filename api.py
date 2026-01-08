from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, time, timedelta
import pytz
import yfinance as yf
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ STATIC FRONTEND (Render-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ---------------- TIMEZONE ----------------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

# ---------------- DATA ----------------
def get_nifty_data():
    ticker = yf.Ticker("^NSEI")
    data = ticker.history(period="1d", interval="5m")
    last = data.iloc[-1]
    spot = round(float(last["Close"]), 2)
    atm = round(spot / 50) * 50
    return spot, atm

def weekly_expiry(d):
    days = (3 - d.weekday()) % 7
    return (d + timedelta(days=days)).strftime("%d %b %Y")

def monthly_expiry(d):
    temp = d.replace(day=28) + timedelta(days=4)
    last = temp - timedelta(days=temp.day)
    while last.weekday() != 3:
        last -= timedelta(days=1)
    return last.strftime("%d %b %Y")

# ---------------- API ----------------
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

    result = {
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry(today),
        "monthly_expiry": monthly_expiry(today)
    }

    if not (start <= now.time() <= end):
        result["status"] = "NO TRADE"
        return result

    spot, atm = get_nifty_data()

    result.update({
        "status": "BUY CALL",
        "spot": spot,
        "atm": atm,
        "probabilities": {
            "upside": 60,
            "downside": 20,
            "volatile": 20
        },
        "trade": {
            "strike": atm,
            "premium": 420,
            "expected_return": 15,
            "risk": 80
        }
    })

    return result
