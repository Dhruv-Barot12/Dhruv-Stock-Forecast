from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta

app = FastAPI()

# Serve frontend files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def serve_home():
    return FileResponse("Frontend/index.html")

@app.get("/trade")
def trade_output():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    weekly_expiry = now + relativedelta(days=(4 - now.weekday()) % 7)
    monthly_expiry = now.replace(day=27)

    data = {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry.strftime("%d %b %Y"),
        "monthly_expiry": monthly_expiry.strftime("%d %b %Y"),
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High",
        "actionable_summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return. "
            "This is a high-risk intraday setup based on momentum. "
            "Strict stop-loss discipline is advised."
        )
    }

    return JSONResponse(data)
