# ai.py
import json, os, asyncio
from typing import Dict, List, Optional
import httpx
from config import settings

# --- Fallback seeds (used if no key or errors) ---
SEED: Dict[str, Dict[str, List[str] | str]] = {
    "happy": {"songs": ["Pharrell Williams – Happy","Daft Punk – Get Lucky","Khalid – Better","Dua Lipa – Levitating","Lizzo – Good as Hell"],
              "images": ["https://picsum.photos/seed/sun/600/400","https://picsum.photos/seed/yellow/600/400","https://picsum.photos/seed/bright/600/400","https://picsum.photos/seed/smile/600/400"],
              "outfits": ["Light denim + white tee + sneakers","Linen shirt + chinos","Pastel hoodie + shorts"],
              "coffee": "Iced vanilla latte"},
    "sad":   {"songs": ["Adele – Someone Like You","Joji – Slow Dancing in the Dark","Billie Eilish – when the party's over","Sam Smith – Too Good at Goodbyes","The 1975 – Somebody Else"],
              "images": ["https://picsum.photos/seed/rain/600/400","https://picsum.photos/seed/blue/600/400","https://picsum.photos/seed/cloud/600/400","https://picsum.photos/seed/window/600/400"],
              "outfits": ["Oversized hoodie + joggers","Dark cardigan + tee","Beanie + flannel"],
              "coffee": "Hot mocha"},
    "chill": {"songs": ["Lauv – I Like Me Better","Kina – Get You the Moon","Post Malone – Circles","Rex Orange County – Sunflower","Clairo – Sofia"],
              "images": ["https://picsum.photos/seed/chill/600/400","https://picsum.photos/seed/soft/600/400","https://picsum.photos/seed/lofi/600/400","https://picsum.photos/seed/quiet/600/400"],
              "outfits": ["Crewneck + relaxed jeans","Flannel + tee","Quarter-zip + cargos"],
              "coffee": "Iced americano"},
}

def _fallback(mood: str) -> Dict[str, List[str] | str]:
    key = (mood or "").strip().lower()
    base = SEED.get(key)
    if base: return base
    return {
        "songs": [f"{(mood or 'mood').title()} Vibes – Track {i}" for i in range(1,6)],
        "images": [f"https://picsum.photos/seed/{key or 'mood'}/{600+i*10}/{400+i*10}" for i in range(4)],
        "outfits": [f"{(mood or 'mood').title()} fit {i}" for i in range(1,4)],
        "coffee": "Latte",
    }

# ---------- LLM prompt ----------
PROMPT = """You are a mood stylist. Gicven the one-word mood "{mood}", produce concise recommendations.
Return STRICT JSON with keys:
- songs: array of 5 strings like "Artist – Title"
- images: array of 4 short scene prompts or aesthetic phrases
- outfits: array of 3 short outfit descriptions
- coffee: single string coffee drink
Return ONLY JSON, no extra text.
"""

# ---------- Small helper: retries + backoff ----------
async def _request_with_retry(client: httpx.AsyncClient, url: str, headers: dict, body: dict,
                              max_attempts: int = 3) -> Optional[httpx.Response]:
    for attempt in range(1, max_attempts + 1):
        r = await client.post(url, headers=headers, json=body)
        if r.is_success:
            return r
        if r.status_code == 401:
            print("OpenAI 401 Unauthorized:", r.text[:200])
            return None
        if r.status_code in (429, 500, 502, 503, 504):
            wait = min(2 ** attempt, 8)
            print(f"OpenAI {r.status_code}. retrying in {wait}s (attempt {attempt}/{max_attempts})")
            await asyncio.sleep(wait)
            continue
        print(f"OpenAI error {r.status_code}:", r.text[:200])
        return None
    return None

# ---------- JSON recs ----------
async def _openai_json(mood: str) -> Optional[Dict[str, List[str] | str]]:
    if not settings.OPENAI_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": PROMPT.format(mood=mood)}
        ],
        "temperature": 0.7
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await _request_with_retry(client, "https://api.openai.com/v1/chat/completions", headers, body)
            if not r:
                return None
            text = r.json()["choices"][0]["message"]["content"]
            data = json.loads(text)
            return {
                "songs": list(data.get("songs", []))[:5],
                "images": list(data.get("images", []))[:4],
                "outfits": list(data.get("outfits", []))[:3],
                "coffee": data.get("coffee", "Latte"),
            }
    except Exception as e:
        print("OpenAI JSON error:", repr(e))
        return None

# ---------- Image generation ----------
async def _openai_images(mood: str, n: int = 4, size: str = "512x512") -> List[str]:
    if not settings.OPENAI_API_KEY:
        return []
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Aesthetic mood board for the mood '{mood}'. Minimal, photographic, editorial style."
    body = {"model": "gpt-image-1", "prompt": prompt, "n": n, "size": size, "response_format": "b64_json"}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await _request_with_retry(client, "https://api.openai.com/v1/images/generations", headers, body)
            if not r:
                return []
            out: List[str] = []
            for d in r.json().get("data", [])[:n]:
                b64 = d.get("b64_json")
                if b64:
                    out.append(f"data:image/png;base64,{b64}")
            return out
    except Exception as e:
        print("OpenAI image error:", repr(e))
        return []

# ---------- Orchestration ----------
async def llm_dayboard(mood: str) -> Dict[str, List[str] | str]:
    mood = (mood or "").strip() or "mood"

    llm = await _openai_json(mood) if settings.OPENAI_API_KEY else None
    base = _fallback(mood)

    songs   = (llm.get("songs")   if llm else None) or base["songs"]
    outfits = (llm.get("outfits") if llm else None) or base["outfits"]
    coffee  = (llm.get("coffee")  if llm else None) or base["coffee"]

    images = await _openai_images(mood, 4, "512x512") if settings.OPENAI_API_KEY else []
    if not images:
        images = (llm.get("images") if llm else None) or base["images"]

    return {
        "songs": songs[:5],
        "images": images[:4],
        "outfits": outfits[:3],
        "coffee": coffee,
    }
