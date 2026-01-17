from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import os
import pyotp

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- TIME ----------------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def fmt(dt):
    return dt.strftime("%d %B %Y, %H:%M IST")

# ---------------- ENV ----------------
def env(key):
    val = os.getenv(key)
    if not val:
        raise HTTPException(status_code=500, detail=f"Missing ENV: {key}")
    return val

# ---------------- SMART API (SAFE LOAD) ----------------
def get_smart_connection():
    try:
        # Import INSIDE function (critical)
        from SmartApi import SmartConnect  

        api_key = env("SMART_API_KEY")
        client = env("SMART_CLIENT_ID")
        password = env("SMART_PASSWORD")
        totp_secret = env("SMART_TOTP")

        smart = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_secret).now()

        session = smart.generateSession(client, password, otp)
        if not session.get("status"):
            raise Exception("SmartAPI session failed")

        return smart

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="SmartAPI library not installed correctly"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- CORE LOGIC ----------------
def probabilities(vix):
    if vix >= 16:
        return 25, 45, 15, 35
    elif vix <= 13:
        return 45, 25, 15, 30
    else:
        return 30, 30, 25, 30

def summary(vix):
    if vix >= 16:
        return (
            "Actionable Summary:\n"
            "Bearish bias with elevated volatility.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM PUT only\n"
            "• Avoid CALL buying\n\n"
            "Risk:\n"
            "• Short covering possible\n"
            "• Use strict stop-loss"
        )
    elif vix <= 13:
        return (
            "Actionable Summary:\n"
            "Bullish bias with controlled volatility.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM CALL only\n"
            "• Avoid PUT buying"
        )
    else:
        return (
            "Actionable Summary:\n"
            "No clear edge.\n"
            "Avoid aggressive trades."
        )

# ---------------- ROUTES ----------------
@app.get("/")
def health():
    return {"status": "API running"}

@app.get("/nifty-930")
def nifty_930():
    try:
        smart = get_smart_connection()

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
            "summary": summary(vix_val),
            "generated_at": fmt(ist_now())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
