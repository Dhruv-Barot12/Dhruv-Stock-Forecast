@app.get("/trade")
def trade():
    now = datetime.now(IST)

    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": now.strftime("%d %b %Y, %I:%M %p IST"),
        "weekly_expiry": weekly_expiry(),
        "monthly_expiry": monthly_expiry(),
        "probabilities": {
            "upside": 60,
            "downside": 20,
            "volatile": 20
        },
        "decision": "BUY CALL",
        "trade": {
            "strike": 25900,
            "premium": 420,
            "expected_return": 15,
            "risk": 8
        },
        "actionable_summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return, "
            "considering the high risk profile and current market conditions. "
            "Monitor the trade closely, as the risk of loss is 8%."
        )
    }
