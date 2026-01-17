from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import os
import pyotp

# ✅ CORRECT IMPORT (case-sensitive)
from smartapi import SmartConnect

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Serve Frontend ----------
app.mount("/Frontend", StaticFiles(directory="Frontend"), name="frontend")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ---------- Helpers ----------
IST = pytz.timezone("Asia/Kolkata")

def ist_now():
    return datetime.now(IST)

def fmt_time(dt):
    return dt.strftime("%d %B %Y, %H:%M IST")

def env(name):
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing ENV variable: {name}")
    return value

# ---------- SmartAPI Login ----------
def smartapi_login():
    try:
        api_key = env("SMART_API_KEY")
        client_id = env("SMART_CLIENT_ID")
        password = env("SMART_PASSWORD")
        totp_secret = env("SMART_TOTP")

        obj = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_secret).now()

        session = obj.generateSession(client_id, password, otp)

        if not session or not session.get("status"):
            raise Exception("SmartAPI session failed")

        return obj

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SmartAPI login error: {str(e)}")

# ---------- Business Logic ----------
def compute_probabilities(vix, bias):
    if bias == "bearish":
        return 25, 45, 15, 35
    if bias == "bullish":
        return 45, 25, 15, 35
    return 30, 30, 25, 30

def build_summary(bias, vix):
    if bias == "bearish":
        return (
            "Actionable Summary:\n"
            "Market shows bearish bias after opening range.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM PUT options only\n"
            "• Avoid CALL buying unless strong reversal\n\n"
            "Risk:\n"
            f"• Volatility elevated (VIX ~ {vix:.2f})\n"
            "• Use strict stop-loss"
        )
    if bias == "bullish":
        return (
            "Actionable Summary:\n"
            "Market shows bullish momentum.\n\n"
            "Trade Plan:\n"
            "• Buy near ATM CALL options only\n"
            "• Avoid PUT buying unless breakdown\n\n"
            "Risk:\n"
            f"• Volatility elevated (VIX ~ {vix:.2f})"
        )
    return (
        "Actionable Summary:\n"
        "Market conditions unclear.\n\n"
        "Trade Plan:\n"
        "• Avoid aggressive trades\n"
    )

# ---------- API ----------
@app.get("/nifty-930")
def execute_930_trade():
    try:
        smart = smartapi_login()

        nifty = smart.ltpData("NSE", "NIFTY", "26000")
        ltp = float(nifty["data"]["ltp"])

        vix_data = smart.ltpData("NSE", "INDIAVIX", "26009")
        vix = float(vix_data["data"]["ltp"])

        bias = "bearish" if vix >= 16 else "neutral"

        up, down, flat, vol = compute_probabilities(vix, bias)
        summary = build_summary(bias, vix)

        return JSONResponse({
            "reference": round(ltp, 2),
            "upside": up,
            "downside": down,
            "flat": flat,
            "volatility": vol,
            "summary": summary,
            "generated_at": fmt_time(ist_now())
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
