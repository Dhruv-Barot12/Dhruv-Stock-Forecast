from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

# Check frontend availability safely
FRONTEND_DIR = "frontend"
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def root():
    if os.path.isfile(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return JSONResponse({"status": "API running"})

@app.get("/health")
def health():
    return {"status": "API running"}

@app.get("/nifty-930-probability")
def nifty_930_probability():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return {
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": (
            "High-risk intraday setup.\n"
            "Directional bias unclear pre-open.\n"
            "Trade only after early confirmation.\n"
            "Avoid holding both CE & PE together."
        ),
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST")
    }
