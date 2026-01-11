from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend folder
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("Frontend/index.html")

@app.get("/trade")
def trade():
    today = datetime.now().strftime("%d January %Y")
    generated = datetime.now().strftime("%d %B %Y, %I:%M %p IST")

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": generated,
        "weekly_expiry": "16 January 2026",
        "monthly_expiry": "27 January 2026",
        "output": f"""
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
