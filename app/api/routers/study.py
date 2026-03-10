from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas.study import (
    AnswerResponse,
    AnswerSubmit,
    CardProgressResponse,
    StudySessionCreate,
    StudySessionResponse,
)
from app.database.models import User
from app.database.session import get_session
from app.services.study import end_session, get_user_progress, start_session, submit_answer

router = APIRouter(prefix="/study", tags=["Study"])


@router.post("/sessions", response_model=StudySessionResponse)
async def create_session(
    data: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await start_session(current_user.id, data.deck_id, session)


@router.post("/sessions/{session_id}/answer", response_model=AnswerResponse)
async def answer_card(
    session_id: UUID,
    answer: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await submit_answer(current_user.id, session_id, answer, session)


@router.post("/sessions/{session_id}/end", response_model=StudySessionResponse)
async def finish_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await end_session(current_user.id, session_id, session)


@router.get("/progress/{deck_id}", response_model=list[CardProgressResponse])
async def get_progress(
    deck_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_user_progress(current_user.id, deck_id, session)
