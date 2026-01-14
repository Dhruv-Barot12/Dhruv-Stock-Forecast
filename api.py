from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
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

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/")
def serve_index():
    return FileResponse(os.path.join("frontend", "index.html"))

# Health check
@app.get("/health")
def health():
    return {"status": "API running"}

# 9:30 Probability API
@app.get("/nifty-930-probability")
def nifty_930_probability():
    now = datetime.now().strftime("%d %B %Y, %I:%M %p IST")

    return {
        "title": "Intraday Probability Outlook — NIFTY 50 (9:30 AM)",
        "reference_level": 25732.3,
        "probabilities": {
            "upside": 40,
            "downside": 40,
            "flat": 20,
            "high_volatility": 30
        },
        "actionable_summary": {
            "strategy": "Buy Puts only (high-risk directional downside play)",
            "reason": "Volatility skewed to downside with weak breadth",
            "recommended_strikes": ["ATM PE", "1-step ITM PE"],
            "expected_premium_range": "₹180–₹260",
            "probability_of_success": "55–60%"
        },
        "generated_at": now
    }
