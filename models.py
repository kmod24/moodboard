# models.py
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    moods: List["Mood"] = Relationship(back_populates="user")


class Mood(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    mood_word: str
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # cached AI output
    songs: Optional[str] = None     # JSON stringified list
    images: Optional[str] = None    # JSON stringified list
    outfits: Optional[str] = None   # JSON stringified list
    coffee: Optional[str] = None

    user: Optional[User] = Relationship(back_populates="moods")
