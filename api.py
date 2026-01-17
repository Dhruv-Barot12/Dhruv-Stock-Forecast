import os
import pytz
import pyotp
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smartapi import SmartConnect


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- UTILITIES ----------

def ist_now():
    return datetime.now(pytz.timezone("Asia/Kolkata"))


def fmt(dt):
    return dt.strftime("%d %B %Y, %H:%M IST")


def probabilities(vix):
    if vix >= 18:
        return 45, 40, 15, 40
    elif vix >= 14:
        return 40, 35, 25, 30
    else:
        return 35, 30, 35, 20


def actionable_summary(vix):
    if vix >= 18:
        return (
            "High volatility expected at open.\n"
            "• Prefer ATM Put buying on breakdown.\n"
            "• Avoid Call buying unless strong opening range breakout.\n"
            "• Expect fast premium expansion — strict stop-loss mandatory.\n"
            "• Suitable only for experienced intraday traders."
        )
    elif vix >= 14:
        return (
            "Moderate volatility expected.\n"
            "• Directional trades possible after confirmation.\n"
            "• ATM options preferred over OTM.\n"
            "• Avoid overtrading — wait for clean structure."
        )
    else:
        return (
            "Low volatility environment.\n"
            "• Directional option buying not advised.\n"
            "• Premium decay likely.\n"
            "• Better to avoid 9:30 trade today."
        )


# ---------- SMART API ----------

def get_smart():
    api_key = os.getenv("SMART_API_KEY")
    client_id = os.getenv("SMART_CLIENT_ID")
    password = os.getenv("SMART_PASSWORD")
    totp_secret = os.getenv("SMART_TOTP")

    smart = SmartConnect(api_key=api_key)

    otp = pyotp.TOTP(totp_secret).now()

    data = smart.generateSession(client_id, password, otp)

    if not data.get("status"):
        raise Exception("SmartAPI login failed")

    return smart


# ---------- ROUTES ----------

@app.get("/")
def health():
    return {"status": "API running"}


@app.get("/nifty-930")
def nifty_930():
    try:
        smart = get_smart()

        nifty = smart.ltpData("NSE", "NIFTY", "26000")
        vix = smart.ltpData("NSE", "INDIAVIX", "26009")

        if not nifty.get("data") or not vix.get("data"):
            raise Exception("Live market data unavailable")

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
            "generated_at": fmt(ist_now())
        }

    except Exception as e:
        return {
            "reference": None,
            "upside": None,
            "downside": None,
            "flat": None,
            "volatility": None,
            "summary": (
                "Live data could not be fetched.\n"
                "• SmartAPI credentials may be invalid\n"
                "• Market may be closed\n"
                "• Please retry after some time"
            ),
            "generated_at": fmt(ist_now()),
            "error": str(e)
        }
