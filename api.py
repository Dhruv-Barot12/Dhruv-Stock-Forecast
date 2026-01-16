from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import pytz

app = FastAPI()

# Serve Frontend folder
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# Serve index.html at root URL
@app.get("/")
def serve_ui():
    return FileResponse("Frontend/index.html")

# 9:30 Trade API
@app.get("/nifty-930")
def nifty_930():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return {
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": "Buy Puts only. Avoid calls unless strong breakout.",
        "generated_at": now.strftime("%d %B %Y, %H:%M IST")
    }
