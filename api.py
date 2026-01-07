from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import os

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
if os.path.exists("Frontend"):
    app.mount("/static", StaticFiles(directory="Frontend"), name="static")

def fetch_nifty_data():
    """Fetch real-time Nifty 50 data from NSE"""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["data"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Nifty data: {str(e)}")

@app.get("/")
def home():
    """Serve the main HTML page"""
    if os.path.exists("Frontend/index.html"):
        return FileResponse("Frontend/index.html")
    return {"message": "Dhruv Stock Forecast API is running"}

@app.get("/support-resistance")
def support_resistance():
    """Get current support and resistance levels"""
    try:
        nifty = fetch_nifty_data()
        return {
            "spot": round(nifty["lastPrice"], 2),
            "support": round(nifty["dayLow"], 2),
            "resistance": round(nifty["dayHigh"], 2),
            "logic": "Day low used as support and day high used as resistance",
            "validity": "Today",
            "disclaimer": "For educational purposes only"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-report")
def generate_report():
    """Generate AI-powered options strategy report using Groq"""
    try:
        # Get current market data
        nifty = fetch_nifty_data()
        spot = round(nifty["lastPrice"], 2)
        atm_strike = round(spot / 50) * 50
        
        # Get Groq API key from environment
        api_key = os.getenv("GROQ_API_KEY", "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")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
        
        # Call Groq API
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are an expert options trader analyzing Nifty 50 intraday opportunities.

Current Market Data:
- Nifty Spot: {spot}
- ATM Strike: {atm_strike}
- Day High: {round(nifty['dayHigh'], 2)}
- Day Low: {round(nifty['dayLow'], 2)}
- Previous Close: {round(nifty['previousClose'], 2)}

Generate a concise intraday options strategy report (200-300 words) with:
1. Market sentiment (bullish/bearish/neutral)
2. Recommended strategy (Call or Put buying)
3. Entry and exit levels
4. Risk management tips

Keep it practical and actionable for today's trading session."""

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(groq_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        ai_report = response.json()["choices"][0]["message"]["content"]
        
        return {
            "success": True,
            "current_spot": spot,
            "atm_strike": atm_strike,
            "report": ai_report,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
