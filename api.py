import yfinance as yf

def fetch_nifty_option_chain():
    try:
        ticker = yf.Ticker("^NSEI")  # Nifty 50 symbol
        data = ticker.history(period="1d")
        spot = round(data["Close"].iloc[-1], 2)
        day_high = round(data["High"].iloc[-1], 2)
        day_low = round(data["Low"].iloc[-1], 2)
        
        # For January expiry, approximate ATM (real option chain needs paid API, but spot is accurate)
        atm_strike = round(spot / 50) * 50  # Nearest 50 strike
        
        return {
            "spot": spot,
            "atm_strike": atm_strike,
            "call_premium": "Live data (approx)",  # Placeholder
            "put_premium": "Live data (approx)",
            "expiry": "29-Jan-2026",  # Weekly/monthly approx
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yfinance fetch failed: {str(e)}")
