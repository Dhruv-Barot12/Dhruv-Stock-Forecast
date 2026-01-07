from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

def get_nifty_data():
    try:
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="2d")
        today = hist.iloc[-1]
        spot = round(today['Close'], 2)
        day_high = round(today['High'], 2)
        day_low = round(today['Low'], 2)
        atm_strike = round(spot / 50) * 50
        return {
            "spot": spot,
            "day_high": day_high,
            "day_low": day_low,
            "atm_strike": atm_strike,
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data error: {str(e)}")

@app.get("/support-resistance")
def support_resistance():
    try:
        data = get_nifty_data()
        return {
            "spot": data["spot"],
            "support": data["day_low"],
            "resistance": data["day_high"],
            "logic": "Day low as support, day high as resistance",
            "validity": "Intraday",
            "disclaimer": "Educational only"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-report")
def generate_report():
    try:
        data = get_nifty_data()
        spot = data["spot"]
        atm_strike = data["atm_strike"]

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY not set"}

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        prompt = f"""Nifty 50 intraday analysis for 07 Jan 2026.
Spot: {spot}
ATM: {atm_strike}
High/Low: {data['day_high']}/{data['day_low']}

Give:
1. Probability (%): higher / lower / volatile
2. Recommended strategy: Buy Calls or Puts
3. Expected return & risks
4. Actionable Summary"""

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        report = response.choices[0].message.content.strip()

        return {
            "success": True,
            "spot": spot,
            "atm_strike": atm_strike,
            "report": report,
            "generated_at": data["timestamp"]
        }
    except Exception as e:
        return {"error": f"AI failed: {str(e)}"}
