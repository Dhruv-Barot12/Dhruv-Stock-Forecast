import yfinance as yf
from datetime import datetime

def fetch_nifty_option_chain():
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
            "atm_strike": atm_strike,
            "call_premium": "Live market",
            "put_premium": "Live market",
            "expiry": "29-Jan-2026",
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")
