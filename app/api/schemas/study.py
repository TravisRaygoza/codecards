from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.database.models import Progress


class StudySessionCreate(BaseModel):
    deck_id: UUID


class AnswerSubmit(BaseModel):
    card_id: UUID
    quality: int  # 0-5 how well they knew it (SM-2 scale)


class AnswerResponse(BaseModel):
    card_id: UUID
    correct: bool
    next_review: datetime
    ease_factor: float
    interval: int


class StudySessionResponse(BaseModel):
    id: UUID
    deck_id: UUID
    total_reviewed: int
    total_correct: int
    started_at: datetime
    completed_at: Optional[datetime] = None


class CardProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    card_id: UUID
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review: datetime
    progress: Progress
