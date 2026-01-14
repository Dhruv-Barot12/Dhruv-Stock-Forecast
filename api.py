from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- PATHS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")

# ---------- STATIC FILES ----------
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ---------- ROOT ----------
@app.get("/")
def serve_index():
    return FileResponse(INDEX_FILE)

# ---------- API STATUS ----------
@app.get("/status")
def status():
    return {"status": "API running"}

# ---------- 9:30 PROBABILITY ----------
@app.get("/nifty-930-probability")
def nifty_930_probability():
    return {
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": (
            "Market is evenly balanced.\n"
            "High-risk traders may wait for first 15-min breakout.\n"
            "Avoid buying both sides simultaneously."
        ),
        "generated_at": datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    }
