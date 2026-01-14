from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import pytz
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "API running"}

@app.get("/nifty-930-probability")
def nifty_930_probability():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return {
        "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": (
            "High-risk setup today.\n"
            "Directional clarity is limited.\n"
            "Trade only after early trend confirmation.\n"
            "Avoid holding both call and put together."
        ),
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST")
    }
