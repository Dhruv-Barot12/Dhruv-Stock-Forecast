from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import pytz

app = FastAPI()

# ✅ Serve Frontend folder as static
app.mount("/Frontend", StaticFiles(directory="Frontend"), name="frontend")

# ✅ Serve index.html at root
@app.get("/")
def serve_home():
    return FileResponse("Frontend/index.html")

# ✅ API endpoint used by app.js
@app.get("/nifty-930")
def nifty_930():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return JSONResponse({
        "reference": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "volatility": 30,
        "summary": "Buy Puts only. Avoid calls unless strong breakout.",
        "generated_at": now.strftime("%d %B %Y, %H:%M IST")
    })
