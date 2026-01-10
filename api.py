@app.get("/api/trade")
def trade_output():
    return {
        "spot": 25876.85,
        "atm": 25900,
        "generated": "10 Jan 2026, 02:41 PM IST",
        "weekly_expiry": "16 Jan 2026",
        "monthly_expiry": "27 Jan 2026",
        "decision": "BUY CALL",
        "premium": 420,
        "expected_return": "15%",
        "risk": "High",
        "summary": (
            "Buy NIFTY 25900 CALL for a potential 15% return. "
            "This is a high-risk intraday setup based on momentum. "
            "Strict stop-loss discipline is advised."
        ),
        "put_section": {
            "title": "Buying Put options only (near ATM)",
            "strike": "25900 PE or 25800 PE (whichever is closer to spot at entry)",
            "premium_range": "₹380–480",
            "expected_return": "130–250% (if Nifty falls 200–400 pts towards 25,600–25,500)"
        },
        "call_section": {
            "title": "Buying Call options only (near ATM)",
            "strike": "25900 CE or 26000 CE",
            "premium_range": "₹410–520",
            "expected_return": "50–120% (requires strong breakout above 26,100 with volume)"
        },
        "actionable_summary": (
            "Recommended strategy today: Buy Puts only (high-risk directional downside play)\n"
            "Avoid buying calls unless explosive breakout above 26,100\n"
            "Do not buy both today (directional bias clear)"
        )
    }
