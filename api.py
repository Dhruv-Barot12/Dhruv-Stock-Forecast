from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import os
from openai import OpenAI

app = FastAPI()  # This line is required!

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("Frontend/index.html")

# ... (keep the rest of your fetch_nifty_data, support-resistance, generate-report functions from previous clean version)
