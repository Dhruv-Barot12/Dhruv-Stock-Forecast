from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pytz

app = FastAPI()

# CORS (safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# Root → index.html
@app.get("/")
def serve_home():
    return FileResponse("Frontend/index.html")

# API for trade data
@app.get("/api/trade")
def trade_output():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": "16 Jan 2026",
        "monthly_expiry": "27 Jan 2026",
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High",
        "summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return. "
            "This is a high-risk intraday setup based on momentum. "
            "Strict stop-loss discipline is advised."
        )
    }

# Support & Resistance (button fix)
@app.get("/api/support-resistance")
def support_resistance():
    return {
        "support": [25750, 25680],
        "resistance": [26020, 26100]
    }

