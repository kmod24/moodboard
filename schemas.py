# schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

# ---- Auth ----
class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str

# ---- Mood input/output ----
class MoodCreate(BaseModel):
    mood_word: str = Field(min_length=1, max_length=30)
    note: Optional[str] = None

class MoodOut(BaseModel):
    id: int
    mood_word: str

class DayboardOut(BaseModel):
    mood_word: str
    songs: List[str]
    images: List[str]
    outfits: List[str]
    coffee: str
