


from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.database.models import CardType


class CardBase(BaseModel):
    front: str
    back: str
    card_type: CardType
    difficulty: int
    code_template: Optional[str] = None
    ai_generated: bool

class CardCreate(CardBase):
    deck_id: UUID

class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    card_type: Optional[CardType] = None
    difficulty: Optional[int] = None
    code_template: Optional[str] = None
    ai_generated: Optional[bool] = None
    
class CardResponse(CardBase):
    id: UUID
    deck_id: UUID
