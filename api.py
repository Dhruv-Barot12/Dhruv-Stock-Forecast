from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import pytz

app = FastAPI()

IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/trade")
def trade():
    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": ist_now(),
        "weekly_expiry": "09 Jan 2026",
        "monthly_expiry": "27 Jan 2026",
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High",
        "actionable_summary": (
            "Buy NIFTY 25900 CALL for a potential 15% intraday return. "
            "High-risk trade. Monitor closely and exit on adverse move."
        )
    }

@app.get("/api/support-resistance")
def support_resistance():
    return {
        "support": "25800",
        "resistance": "26100"
    }
