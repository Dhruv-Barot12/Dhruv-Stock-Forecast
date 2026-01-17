from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import os
import pyotp

# SmartAPI (Angel One)
from smartapi import SmartConnect

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- TIME --------------------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def fmt_time(dt):
    return dt.strftime("%d %B %Y, %H:%M IST")

# -------------------- ENV --------------------
def env(name):
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing ENV: {name}")
    return value

# -------------------- SMART API LOGIN --------------------
def smartapi_login():
    try:
        api_key = env("SMART_API_KEY")
        client_id = env("SMART_CLIENT_ID")
        password = env("SMART_PASSWORD")
        totp_secret = env("SMART_TOTP")

        smart = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_secret).now()

        session = smart.generateSession(client_id, password, otp)
        if not session or not session.get("status"):
            raise Exception("SmartAPI session failed")

        return smart

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- LOGIC --------------------
def probabilities(vix):
    if vix >= 16:
        return 25, 45, 15, 35  # bearish
    elif vix <= 13:
        return 45, 25, 15, 30  # bullish
    else:
        return 30, 30, 25, 30  # neutral

def actionable_summary(vix):
    if vix >= 16:
        return (
            "Actionable Summary:\n"
            "Market shows bearish bias with elevated volatility.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM PUT options only\n"
            "• Avoid CALL buying unless strong reversal\n\n"
            "Risk:\n"
            "• Sudden short-covering rallies possible\n"
            "• Strict stop-loss mandatory"
        )
    elif vix <= 13:
        return (
            "Actionable Summary:\n"
            "Market shows bullish momentum with controlled volatility.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM CALL options only\n"
            "• Avoid PUT buying unless breakdown\n\n"
            "Risk:\n"
            "• Watch for fake breakouts"
        )
    else:
        return (
            "Actionable Summary:\n"
            "Market conditions are unclear.\n\n"
            "Trade Plan:\n"
            "• Avoid aggressive directional trades"
        )

# -------------------- ROUTES --------------------
@app.get("/")
def health():
    return {"status": "API running"}

@app.get("/nifty-930")
def nifty_930():
    try:
        smart = smartapi_login()

        nifty = smart.ltpData("NSE", "NIFTY", "26000")
        vix = smart.ltpData("NSE", "INDIAVIX", "26009")

        ltp = float(nifty["data"]["ltp"])
        vix_val = float(vix["data"]["ltp"])

        up, down, flat, vol = probabilities(vix_val)

        return {
            "reference": round(ltp, 2),
            "upside": up,
            "downside": down,
            "flat": flat,
            "volatility": vol,
            "summary": actionable_summary(vix_val),
            "generated_at": fmt_time(ist_now())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
