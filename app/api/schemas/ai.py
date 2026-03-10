from pydantic import BaseModel

from app.database.models import CardType, Language, Topic


class GenerateCardsRequest(BaseModel):
    topic: Topic
    language: Language
    card_type: CardType
    difficulty: int  # 1-5
    count: int = 5  # how many cards to generate


class GeneratedCard(BaseModel):
    front: str
    back: str
    code_template: str | None = None
    difficulty: int
