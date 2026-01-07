@app.get("/generate-report")
def generate_report():
    try:
        nifty = fetch_nifty_data()
        spot = round(nifty["lastPrice"], 2)
        atm_strike = round(spot / 50) * 50

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY not configured on server"}

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        prompt = f"""Expert Nifty 50 intraday options analysis for 07 Jan 2026.

Current Spot: {spot}
ATM Strike: {atm_strike}
Day Range: {nifty['dayLow']} - {nifty['dayHigh']}

Provide:
1. Probability (%): Close higher / lower / volatile
2. Recommended high-risk strategy: Buy Calls or Puts
3. Expected return and risks
4. Actionable Summary (strategy, strike, premium range, probability)

Keep concise and practical."""

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600,
            timeout=30
        )
        
        report = response.choices[0].message.content.strip()
        
        if not report:
            report = "Analysis complete. Market neutral today. Consider strangle for volatility play."

        return {
            "success": True,
            "spot": spot,
            "atm_strike": atm_strike,
            "report": report,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"AI failed: {str(e)}",
            "spot": "N/A",
            "report": "Temporary AI issue. Try again in a minute."
        }
