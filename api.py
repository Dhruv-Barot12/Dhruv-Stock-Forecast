from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_nifty_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url)
    data = response.json()
    return data["data"][0]

@app.get("/")
def home():
    return {"message": "Dhruv Stock Forecast API is running"}

@app.get("/market-bias")
def market_bias():
    nifty = fetch_nifty_data()

    prev_close = nifty["previousClose"]
    today_open = nifty["open"]

    gap_percent = round(((today_open - prev_close) / prev_close) * 100, 2)

    if today_open > prev_close:
        bias = "Bullish 📈"
        reason = "Market opened above previous close, indicating buying interest"
    else:
        bias = "Bearish 📉"
        reason = "Market opened below previous close, indicating selling pressure"

    if abs(gap_percent) > 0.5:
        confidence = "High"
    elif abs(gap_percent) > 0.2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "market_bias": bias,
        "confidence": confidence,
        "gap_percent": gap_percent,
        "reason": reason,
        "validity": "Today",
        "disclaimer": "For educational purposes only"
    }
