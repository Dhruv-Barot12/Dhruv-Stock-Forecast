from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import pytz
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend folder
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

IST = pytz.timezone("Asia/Kolkata")


# ✅ ROOT SHOULD SERVE UI (NOT JSON)
@app.get("/")
def serve_ui():
    return FileResponse("Frontend/index.html")


# Health check (move API status here)
@app.get("/health")
def health():
    return {"status": "API running"}


@app.get("/nifty-930-probability")
def nifty_probability():

    now = datetime.now(IST)

    reference_level = 25732.3

    upside = 40
    downside = 40
    flat = 20
    high_vol = 30

    if downside > upside:
        action = (
            "Buy PUT options only (high-risk intraday).\n"
            "Avoid CALL buying unless sharp reversal.\n"
            "Do not buy both sides today."
        )
    elif upside > downside:
        action = (
            "Buy CALL options only (high-risk intraday).\n"
            "Avoid PUT buying unless breakdown.\n"
            "Do not buy both sides today."
        )
    else:
        action = (
            "Market balanced.\n"
            "Only scalping trades advised.\n"
            "Avoid positional option buying."
        )

    return {
        "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
        "reference_level": reference_level,
        "probabilities": {
            "upside": upside,
            "downside": downside,
            "flat": flat,
            "high_volatility": high_vol
        },
        "actionable_summary": action,
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST")
    }
