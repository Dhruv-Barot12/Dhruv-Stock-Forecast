from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/trade")
def trade_output():
    today = datetime.now().strftime("%d %B %Y")

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": datetime.now().strftime("%d %B %Y, %I:%M %p IST"),
        "weekly_expiry": "16 January 2026",
        "monthly_expiry": "27 January 2026",

        "strategy_text": f"""
1- Buying Put options only (near ATM)

Recommended strike: 25900 PE or 25800 PE (whichever is closer to spot at entry)
Approx premium range (early-mid session): ₹380–480
Expected return potential: 130–250%
(if Nifty falls 200–400 pts towards 25,600–25,500)

2- Buying Call options only (near ATM)

Recommended strike: 25900 CE or 26000 CE
Approx premium range: ₹410–520
Expected return potential: 50–120%
(requires strong breakout above 26,100 with volume)

Actionable Summary – {today}

Recommended strategy today:
• Buy Puts only (high-risk directional downside play)
• Avoid buying calls unless explosive breakout above 26,100
• Do not buy both today (directional bias clear)
"""
    }

@app.get("/")
def root():
    return {"status": "API running"}
