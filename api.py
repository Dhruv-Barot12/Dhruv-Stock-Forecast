from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import pytz
import os

app = FastAPI()

# Serve frontend static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

IST = pytz.timezone("Asia/Kolkata")

# -------------------------------
# Homepage route (THIS FIXES 404)
# -------------------------------
@app.get("/")
def serve_frontend():
    return FileResponse("Frontend/index.html")

# -------------------------------
# Utility functions
# -------------------------------
def get_weekly_expiry(today):
    days_ahead = 3 - today.weekday()  # Thursday
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def get_monthly_expiry(today):
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    while last_day.weekday() != 3:
        last_day -= timedelta(days=1)
    return last_day

# -------------------------------
# Trade API
# -------------------------------
@app.get("/trade")
def trade_output():
    now = datetime.now(IST)

    if not ("09:20" <= now.strftime("%H:%M") <= "09:28"):
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

