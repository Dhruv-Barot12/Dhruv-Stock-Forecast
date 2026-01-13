@app.get("/api/options-report")
def options_report():
    try:
        # Fetch real-time Nifty data
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="1d")
        today = hist.iloc[-1]
        spot = round(today['Close'], 2)
        day_high = round(today['High'], 2)
        day_low = round(today['Low'], 2)
        atm_strike = round(spot / 50) * 50

        # Get Groq API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY not set"}

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        prompt = f"""You are an expert financial analyst specializing in the Indian equity and derivatives markets, especially Nifty 50 options. The current Nifty 50 index level is {spot}. Using a combination of:
  • Technical analysis (candlestick patterns, intraday indicators, support/resistance, implied volatility, option Greeks, etc.)
  • Fundamental analysis (macroeconomic cues, FII/DII flows, sectoral news, global markets impact)
  • Real-time news sentiment (headlines, corporate announcements, RBI commentary, geopolitical developments)
produce a short report with intraday probability estimates (in percentages) for whether Nifty 50 will move:
  1. Upside
  2. Downside
  3. volatile market ( market maybe goes big up or down)
Specifically:
  1. Starting from the current index level of {spot}, calculate the probability (in %) that the index will finish the trading day higher, lower, or roughly flat. Clearly state your assumptions (e.g., what technical patterns or news you’re emphasizing).
  2. Based on those probabilities, recommend which option-buying near ATM call and put is likely to yield the highest expected profit today:
Buying call options only near ATM
Buying put options only near ATM
     For each strategy, estimate the expected return (percentage) and mention any major risks (e.g., sudden volatility spikes, unexpected news).
I want to trade between 9:30 am and 3:00 pm. Let’s assume a high-risk approach. I will take the January monthly expiry, which will be 27th January monthly 2026.
At the end, provide a concise “Actionable Summary”:
  • Which specific strategy should I execute today, 07th Jan 2026—buy calls, buy puts or both buy?
  • Which strike(s) would you choose if you were trading intraday?
  • Approximately what premium (₹) and probability (%) does each recommended position carry?"""

        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        report = response.choices[0].message.content

        return {
            "success": True,
            "spot": spot,
            "day_high": day_high,
            "day_low": day_low,
            "atm_strike": atm_strike,
            "report": report,
            "generated_at": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p IST")
        }
    except Exception as e:
        return {"error": f"Report failed: {str(e)}"}
