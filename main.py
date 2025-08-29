# main.py
import json
from typing import List, Optional


from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, create_engine, select


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException

from config import settings
from models import User, Mood
from schemas import RegisterIn, LoginIn, TokenOut, MoodCreate, MoodOut, DayboardOut
from security import hash_password, verify_password, create_jwt, decode_jwt
from ai import llm_dayboard

security = HTTPBearer()

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

app = FastAPI(
    title="Mood Dayboard API",
    version="0.1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"ok": True}

def get_db():
    with Session(engine) as s:
        yield s

def auth_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> int:
    token = (credentials.credentials or "").strip()
    if token.startswith("Bearer "):            # tolerate double-Bearer
        token = token.split(" ", 1)[1]
    return decode_jwt(token)



# ---------- Auth ----------
@app.post("/auth/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    u = User(email=body.email, password_hash=hash_password(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return TokenOut(access_token=create_jwt(u.id))

@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.exec(select(User).where(User.email == body.email)).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_jwt(u.id))

# ---------- Mood ----------
@app.post("/moods", response_model=DayboardOut)
async def create_mood(
    payload: MoodCreate,
    user_id: int = Depends(auth_user),
    db: Session = Depends(get_db),
):
    recs = await llm_dayboard(payload.mood_word)
    m = Mood(
        user_id=user_id,
        mood_word=payload.mood_word,
        note=payload.note,
        songs=json.dumps(recs["songs"]),
        images=json.dumps(recs["images"]),
        outfits=json.dumps(recs["outfits"]),
        coffee=recs["coffee"],
    )
    db.add(m); db.commit(); db.refresh(m)
    return DayboardOut(
        mood_word=m.mood_word,
        songs=json.loads(m.songs or "[]"),
        images=json.loads(m.images or "[]"),
        outfits=json.loads(m.outfits or "[]"),
        coffee=m.coffee or "Latte",
    )

@app.get("/moods", response_model=List[MoodOut])
def list_moods(user_id: int = Depends(auth_user), db: Session = Depends(get_db)):
    moods = db.exec(select(Mood).where(Mood.user_id == user_id).order_by(Mood.created_at.desc())).all()
    return [MoodOut(id=m.id, mood_word=m.mood_word) for m in moods]

@app.get("/moods/{mood_id}", response_model=DayboardOut)
def get_mood(mood_id: int, user_id: int = Depends(auth_user), db: Session = Depends(get_db)):
    m = db.get(Mood, mood_id)
    if not m or m.user_id != user_id:
        raise HTTPException(status_code=404, detail="Not found")
    return DayboardOut(
        mood_word=m.mood_word,
        songs=json.loads(m.songs or "[]"),
        images=json.loads(m.images or "[]"),
        outfits=json.loads(m.outfits or "[]"),
        coffee=m.coffee or "Latte",
    )
