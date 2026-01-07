from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import os

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """Serve the main HTML page"""
    return FileResponse("Frontend/index.html")

@app.get("/support-resistance")
def support_resistance():
    """Get current support and resistance levels"""
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        nifty = response.json()["data"][0]
        
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
    """Generate AI-powered options strategy report"""
    try:
        # Get Nifty data
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        nifty = response.json()["data"][0]
        
        spot = round(nifty["lastPrice"], 2)
        atm_strike = round(spot / 50) * 50
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY", "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")
        
        # Call Groq AI
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        groq_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are an expert options trader. Current Nifty Spot: {spot}, ATM: {atm_strike}, High: {round(nifty['dayHigh'], 2)}, Low: {round(nifty['dayLow'], 2)}

Generate a 200-word intraday options strategy with:
1. Market sentiment
2. Call or Put recommendation
3. Entry/exit levels
4. Risk tips"""

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        ai_response = requests.post(groq_url, json=payload, headers=groq_headers, timeout=30)
        ai_response.raise_for_status()
        
        report = ai_response.json()["choices"][0]["message"]["content"]
        
        return {
            "success": True,
            "current_spot": spot,
            "atm_strike": atm_strike,
            "report": report,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }
