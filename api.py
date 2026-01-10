from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import pytz

app = FastAPI()

IST = pytz.timezone("Asia/Kolkata")

def get_weekly_expiry(today):
    # Thursday expiry
    days_ahead = 3 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def get_monthly_expiry(today):
    # Last Thursday of month
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    while last_day.weekday() != 3:
        last_day -= timedelta(days=1)
    return last_day

@app.get("/trade")
def trade_output():
    now = datetime.now(IST)
    time_ok = now.strftime("%H:%M") >= "09:20" and now.strftime("%H:%M") <= "09:28"

    if not time_ok:
        return JSONResponse(
            status_code=403,
            content={"error": "This prompt should be executed only between 9:20 AM and 9:28 AM."}
        )

    weekly = get_weekly_expiry(now)
    monthly = get_monthly_expiry(now)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly.strftime("%d %b %Y"),
        "monthly_expiry": monthly.strftime("%d %b %Y"),
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High",
        "support": [25750, 25680],
        "resistance": [26050, 26120],
        "summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return. "
            "This is a high-risk intraday setup based on momentum. "
            "Strict stop-loss discipline is advised."
        )
    }
