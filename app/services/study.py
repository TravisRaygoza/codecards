from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.models import (
    Card,
    CardProgress,
    Deck,
    Progress,
    ReviewLog,
    StudySession,
)
from app.api.schemas.study import AnswerSubmit
from app.services.sm2 import calculate_sm2


async def start_session(user_id: UUID, deck_id: UUID, session: AsyncSession):
    # 1. Make sure the deck exists
    statement = select(Deck).where(Deck.id == deck_id)
    result = await session.execute(statement)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    # 2. Count the cards in the deck
    statement = select(Card).where(Card.deck_id == deck_id)
    result = await session.execute(statement)
    cards = result.scalars().all()

    if not cards:
        raise HTTPException(status_code=400, detail="Deck has no cards")

    # 3. Create the study session
    study_session = StudySession(
        user_id=user_id,
        deck_id=deck_id,
        total_reviewed=0,
        total_correct=0,
    )

    session.add(study_session)
    await session.commit()
    await session.refresh(study_session)

    return study_session


async def submit_answer(
    user_id: UUID,
    session_id: UUID,
    answer: AnswerSubmit,
    session: AsyncSession,
):
    # 1. Make sure the study session exists and belongs to this user
    statement = select(StudySession).where(StudySession.id == session_id)
    result = await session.execute(statement)
    study_session = result.scalar_one_or_none()

    if not study_session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if study_session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your session")

    # 2. Make sure the card exists
    statement = select(Card).where(Card.id == answer.card_id)
    result = await session.execute(statement)
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # 3. Get or create CardProgress for this user + card
    statement = select(CardProgress).where(
        CardProgress.user_id == user_id,
        CardProgress.card_id == answer.card_id,
    )
    result = await session.execute(statement)
    progress = result.scalar_one_or_none()

    if not progress:
        progress = CardProgress(
            user_id=user_id,
            card_id=answer.card_id,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            progress=Progress.not_started,
        )

    # 4. Run SM-2 algorithm
    sm2_result = calculate_sm2(
        quality=answer.quality,
        repetitions=progress.repetitions,
        ease_factor=progress.ease_factor,
        interval=progress.interval_days,
    )

    # 5. Update card progress with SM-2 results
    progress.ease_factor = sm2_result["ease_factor"]
    progress.interval_days = sm2_result["interval"]
    progress.repetitions = sm2_result["repetitions"]
    progress.next_review = sm2_result["next_review"]
    progress.progress = Progress.completed if answer.quality >= 3 else Progress.in_progress

    session.add(progress)

    # 6. Create review log
    correct = answer.quality >= 3
    review_log = ReviewLog(
        user_id=user_id,
        card_id=answer.card_id,
        session_id=session_id,
        rating=answer.quality,
    )

    session.add(review_log)

    # 7. Update session counters
    study_session.total_reviewed += 1
    if correct:
        study_session.total_correct += 1

    session.add(study_session)

    await session.commit()
    await session.refresh(progress)

    return {
        "card_id": answer.card_id,
        "correct": correct,
        "next_review": sm2_result["next_review"],
        "ease_factor": sm2_result["ease_factor"],
        "interval": sm2_result["interval"],
    }


async def end_session(user_id: UUID, session_id: UUID, session: AsyncSession):
    # 1. Find the session
    statement = select(StudySession).where(StudySession.id == session_id)
    result = await session.execute(statement)
    study_session = result.scalar_one_or_none()

    if not study_session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if study_session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your session")

    # 2. Mark as completed
    study_session.completed_at = datetime.now()

    session.add(study_session)
    await session.commit()
    await session.refresh(study_session)

    return study_session


async def get_user_progress(user_id: UUID, deck_id: UUID, session: AsyncSession):
    """Get progress for all cards in a deck for a specific user"""
    # Get all cards in the deck
    statement = select(Card).where(Card.deck_id == deck_id)
    result = await session.execute(statement)
    cards = result.scalars().all()

    card_ids = [card.id for card in cards]

    # Get progress for those cards
    statement = select(CardProgress).where(
        CardProgress.user_id == user_id,
        CardProgress.card_id.in_(card_ids),
    )
    result = await session.execute(statement)
    progress_list = result.scalars().all()

    return progress_list
