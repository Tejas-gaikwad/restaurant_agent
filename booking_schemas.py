from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Intent(str, Enum):
    book = "book"
    modify = "modify"
    cancel = "cancel"
    menu = "menu"
    other = "other"

class BookingIntent(BaseModel):
    intent: Intent
    name: Optional[str] = None
    date: Optional[str] = None        # YYYY-MM-DD
    time: Optional[str] = None        # HH:MM 24h
    party_size: Optional[int] = None
