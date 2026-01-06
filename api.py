from fastapi import FastAPI
import requests

app = FastAPI()

NIFTY_API_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_nifty_data():
    session = requests.Session()
    session.headers.update(headers)

    response = session.get(NIFTY_API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    nifty = data["data"][0]

    return {
        "lastPrice": nifty["lastPrice"],
        "dayHigh": nifty["dayHigh"],
        "dayLow": nifty["dayLow"],
    }


@app.get("/")
def root():
    return {"message": "Dhruv Stock Forecast API is running"}


@app.get("/support-resistance")
def support_resistance():
    try:
        nifty = fetch_nifty_data()

        return {
            "spot": round(nifty["lastPrice"], 2),
            "support": round(nifty["dayLow"], 2),
            "resistance": round(nifty["dayHigh"], 2),
            "logic": "Day low used as support and day high used as resistance",
            "validity": "Today",
            "disclaimer": "For educational purposes only",
        }

    except Exception as e:
        return {
            "error": "Failed to calculate support & resistance",
            "details": str(e)
        }
