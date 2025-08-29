# simple_main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ai import llm_dayboard  # uses your existing ai.py seed data

app = FastAPI(title="Mood Dayboard (No Auth)", version="1.0")

# allow the page to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"ok": True}

@app.post("/dayboard")
async def dayboard(payload: dict):
    mood = str(payload.get("mood_word", "")).strip()
    recs = await llm_dayboard(mood)
    return {
        "mood_word": mood or "mood",
        "songs": recs["songs"],
        "images": recs["images"],
        "outfits": recs["outfits"],
        "coffee": recs["coffee"],
    }

# serve your index.html from the project folder
ROOT = Path(__file__).parent
app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="static")
