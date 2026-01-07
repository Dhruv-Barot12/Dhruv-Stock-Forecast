from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
app = FastAPI()
# 🔑 CORS FIX (THIS WAS MISSING OR MISPLACED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def fetch_nifty_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["data"][0]
@app.get("/")
def home():
    return {"message": "Dhruv Stock Forecast API is running"}
@app.get("/support-resistance")
def support_resistance():
    nifty = fetch_nifty_data()
    return {
        "spot": round(nifty["lastPrice"], 2),
        "support": round(nifty["dayLow"], 2),
        "resistance": round(nifty["dayHigh"], 2),
        "logic": "Day low used as support and day high used as resistance",
        "validity": "Today",
        "disclaimer": "For educational purposes only"
    }
