@app.get("/support-resistance")
def support_resistance():
    nifty = fetch_nifty_data()

    support = round(nifty["dayLow"], 2)
    resistance = round(nifty["dayHigh"], 2)
    spot = round(nifty["lastPrice"], 2)

    return {
        "spot": spot,
        "support": support,
        "resistance": resistance,
        "logic": "Day low used as support and day high used as resistance",
        "validity": "Today",
        "disclaimer": "For educational purposes only"
    }
