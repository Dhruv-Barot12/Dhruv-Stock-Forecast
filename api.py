from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
import pytz

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("Frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/trade")
def trade():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": "09 Jan 2026",
        "monthly_expiry": "27 Jan 2026",
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High"
    }
