from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "API running"}

@app.get("/nifty-930-probability")
def nifty_930_probability():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    data = {
        "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": (
            "High-risk setup today. Directional clarity is low.\n"
            "Preferred approach: wait for early trend confirmation.\n"
            "Aggressive traders may buy near-ATM options only after breakout.\n"
            "Avoid holding both call and put simultaneously."
        ),
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST")
    }

    return data
