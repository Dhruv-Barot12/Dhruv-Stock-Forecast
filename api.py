from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# Serve frontend
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    file_path = os.path.join("Frontend", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Health check
@app.get("/health")
def health():
    return {"status": "API running"}

# 🔥 9:30 Probability API (NO undefined)
@app.get("/api/nifty-930")
def nifty_930():
    return JSONResponse({
        "reference_level": 25732.3,
        "upside": 40,
        "downside": 40,
        "flat": 20,
        "high_volatility": 30,
        "actionable_summary": "Buy Puts only. Avoid calls unless strong breakout.",
        "generated_at": datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    })
