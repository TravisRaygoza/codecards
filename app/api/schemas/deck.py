from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.database.models import Language, Topic

class DeckBase(BaseModel):
    title: str
    description: str 
    language: Language
    topic: Topic 
    is_public: bool 

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    title: Optional [str] = None
    description: Optional [str] = None 
    language: Optional [Language] = None 
    topic: Optional [Topic] = None 
    is_public: Optional [bool] = None 
    

class DeckResponse(DeckBase):
    id: UUID
    created_at: datetime
    user_id: UUID 


