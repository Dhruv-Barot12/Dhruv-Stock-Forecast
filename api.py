from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IST = pytz.timezone("Asia/Kolkata")


def weekly_expiry():
    today = datetime.now(IST)
    days_ahead = (3 - today.weekday()) % 7  # Thursday
    expiry = today + timedelta(days=days_ahead)
    return expiry.strftime("%d %b %Y")


def monthly_expiry():
    today = datetime.now(IST)
    year = today.year
    month = today.month

    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    while last_day.weekday() != 3:  # Thursday
        last_day -= timedelta(days=1)

    return last_day.strftime("%d %b %Y")


@app.get("/support-resistance")
def support_resistance():
    return {
        "support": [25650, 25580],
        "resistance": [25950, 26050]
    }


@app.get("/trade")
def trade():
    now = datetime.now(IST)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry(),
        "monthly_expiry": monthly_expiry(),
        "probabilities": {
            "upside": 60,
            "downside": 20,
            "volatile": 20
        },
        "decision": "BUY CALL",
        "trade": {
            "strike": 25900,
            "premium": 420,
            "expected_return": 15,
            "risk": 8
        },
        "actionable_summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return, considering the high risk profile "
            "and current market conditions. Monitor the trade closely, as the risk of loss is 8%."
        )
    }
