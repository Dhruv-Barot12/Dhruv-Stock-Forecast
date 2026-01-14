from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IST = pytz.timezone("Asia/Kolkata")

@app.get("/")
def health():
    return {"status": "API running"}

@app.get("/nifty-930-probability")
def nifty_probability():

    now = datetime.now(IST)

    # ---- SAFE BASE DATA (replace later with live feed) ----
    reference_level = 25732.3

    upside = 40
    downside = 40
    flat = 20
    high_vol = 30

    # ---- LOGIC FOR ACTIONABLE SUMMARY ----
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
