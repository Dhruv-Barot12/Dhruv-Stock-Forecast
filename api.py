from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS (important for frontend fetch)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "API running"}

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
            "reason": "Equal upside/downside probability with elevated volatility skewed to downside",
            "recommended_strikes": ["ATM PE", "1-step ITM PE"],
            "expected_premium_range": "₹180 – ₹260",
            "probability_of_success": "55–60%"
        },

        "generated_at": now
    }
