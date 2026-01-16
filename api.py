from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

app = FastAPI()

# Serve frontend folder
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("Frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/nifty-930")
def nifty_930():
    return {
        "index": "NIFTY 50",
        "reference": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "volatility": 30,
        "summary": "Buy Puts only. Avoid calls unless strong breakout.",
        "generated": datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    }
