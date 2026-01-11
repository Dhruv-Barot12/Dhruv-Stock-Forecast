from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")


@app.get("/api/trade")
def trade_output():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %B %Y, %I:%M %p IST"),
        "weekly_expiry": "16 Jan 2026",
        "monthly_expiry": "27 Jan 2026",

        "put_strategy": {
            "title": "Buying PUT options only (near ATM)",
            "strikes": "25900 PE or 25800 PE (closest to spot)",
            "premium": "₹380–480",
            "return": "130–250% (if Nifty falls 200–400 pts towards 25,600–25,500)"
        },

        "call_strategy": {
            "title": "Buying CALL options only (near ATM)",
            "strikes": "25900 CE or 26000 CE",
            "premium": "₹410–520",
            "return": "50–120% (requires strong breakout above 26,100 with volume)"
        },

        "actionable_summary": (
            "Recommended strategy today: Buy PUTs only (high-risk directional downside play). "
            "Avoid buying CALLs unless there is an explosive breakout above 26,100 with strong volume. "
            "Do not buy both sides today — directional bias is clearly bearish."
        )
    }


@app.get("/api/support-resistance")
def support_resistance():
    return {
        "support": [25750, 25600, 25500],
        "resistance": [26000, 26100, 26200]
    }
