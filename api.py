from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import os
import pyotp

# SmartAPI (Angel One)
from SmartApi import SmartConnect

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
    val = os.getenv(name)
    if not val:
        raise HTTPException(status_code=500, detail=f"Missing env var: {name}")
    return val

# ---------- SmartAPI Login ----------
def smartapi_login():
    try:
        api_key = env("SMART_API_KEY")
        client_id = env("SMART_CLIENT_ID")
        password = env("SMART_PASSWORD")
        totp_secret = env("SMART_TOTP")

        sc = SmartConnect(api_key=api_key)
        otp = pyotp.TOTP(totp_secret).now()
        session = sc.generateSession(client_id, password, otp)

        if not session or not session.get("status"):
            raise Exception("Session generation failed")

        return sc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SmartAPI login error: {str(e)}")

# ---------- Core Logic ----------
def compute_probabilities(vix, bias):
    # Conservative, transparent mapping
    if bias == "bearish":
        return 25, 45, 15, 35 if vix >= 15 else 30
    if bias == "bullish":
        return 45, 25, 15, 35 if vix >= 15 else 30
    # neutral
    return 30, 30, 25, 30 if vix >= 15 else 25

def build_summary(bias, vix):
    if bias == "bearish":
        return (
            "Actionable Summary:\n"
            "Market shows a bearish bias after the opening phase.\n"
            "Selling pressure is dominant with risk of further downside if momentum continues.\n\n"
            "Trade Plan:\n"
            "• Prefer buying near ATM PUT options only\n"
            "• Avoid CALL buying unless price reclaims VWAP with strong volume\n"
            "• Best window: 9:30–11:30 AM\n\n"
            "Risk Note:\n"
            f"• Volatility is {'elevated' if vix >= 15 else 'moderate'} (VIX ~ {vix:.2f})\n"
            "• Use strict stop-loss; sudden short covering can cause spikes"
        )
    if bias == "bullish":
        return (
            "Actionable Summary:\n"
            "Market shows a bullish bias with improving momentum.\n"
            "Upside continuation is favored if strength sustains above intraday pivots.\n\n"
            "Trade Plan:\n"
            "• Prefer buying near ATM CALL options only\n"
            "• Avoid PUT buying unless breakdown below support\n"
            "• Best window: 9:30–11:30 AM\n\n"
            "Risk Note:\n"
            f"• Volatility is {'elevated' if vix >= 15 else 'moderate'} (VIX ~ {vix:.2f})\n"
            "• Watch for false breakouts near resistance"
        )
    # neutral
    return (
        "Actionable Summary:\n"
        "Market conditions are mixed with no clear directional edge.\n"
        "Range-bound behavior is likely in the absence of strong triggers.\n\n"
        "Trade Plan:\n"
        "• Avoid aggressive directional trades\n"
        "• Wait for confirmation or stay light\n\n"
        "Risk Note:\n"
        f"• Volatility is {'elevated' if vix >= 15 else 'low-to-moderate'} (VIX ~ {vix:.2f})"
    )

# ---------- API ----------
@app.get("/nifty-930")
def execute_930_trade():
    try:
        sc = smartapi_login()

        # NIFTY spot (symbol token 26000)
        nifty = sc.ltpData("NSE", "NIFTY", "26000")
        ltp = float(nifty["data"]["ltp"])

        # India VIX (symbol token 26009)
        vix_data = sc.ltpData("NSE", "INDIAVIX", "26009")
        vix = float(vix_data["data"]["ltp"])

        # Simple bias logic (transparent)
        # You can extend with ORB/VWAP/OI later without changing UI
        bias = "neutral"
        if vix >= 16:
            bias = "bearish" if ltp < round(ltp, -1) else "bullish"

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
