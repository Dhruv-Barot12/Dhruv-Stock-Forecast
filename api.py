from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time, timedelta
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IST = pytz.timezone("Asia/Kolkata")


def get_expiry_dates():
    today = datetime.now(IST).date()

    # Weekly expiry = next Thursday
    days_to_thu = (3 - today.weekday()) % 7
    weekly_expiry = today + timedelta(days=days_to_thu)

    # Monthly expiry = last Thursday of month
    month_end = today.replace(day=28) + timedelta(days=4)
    last_day = month_end - timedelta(days=month_end.day)
    monthly_expiry = last_day - timedelta(days=(last_day.weekday() - 3) % 7)

    return weekly_expiry, monthly_expiry


@app.get("/trade-930")
def trade_930():
    now = datetime.now(IST).time()

    start = time(9, 20)
    end = time(9, 28)

    weekly_expiry, monthly_expiry = get_expiry_dates()

    # ❌ BLOCK execution outside time window
    if not (start <= now <= end):
        return {
            "status": "NO_TRADE",
            "message_en": "This prompt should be executed only between 9:20 AM and 9:28 AM.",
            "message_hi": "यह प्रॉम्प्ट केवल सुबह 9:20 बजे से 9:28 बजे के बीच ही चलाया जाना चाहिए।",
            "generated": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
            "weekly_expiry": weekly_expiry.strftime("%d %b %Y"),
            "monthly_expiry": monthly_expiry.strftime("%d %b %Y"),
        }

    # ✅ Allowed execution window
    return {
        "status": "TRADE",
        "spot": 25876.85,
        "atm": 25900,
        "probabilities": {
            "upside": 60,
            "downside": 20,
            "volatile": 20,
        },
        "decision": "BUY CALL",
        "strike": 25900,
        "premium": 420,
        "expected_return": 15,
        "risk": 80,
        "generated": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry.strftime("%d %b %Y"),
        "monthly_expiry": monthly_expiry.strftime("%d %b %Y"),
    }
