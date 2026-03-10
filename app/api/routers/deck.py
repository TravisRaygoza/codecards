from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas.deck import DeckCreate, DeckUpdate, DeckResponse
from app.database.models import User
from app.database.session import get_session
from app.services.deck import (
    create_deck,
    get_user_decks,
    get_deck,
    update_deck,
    delete_deck,
)

router = APIRouter(prefix="/decks", tags=["Decks"])


@router.post("/", response_model=DeckResponse)
async def create(
    deck_data: DeckCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await create_deck(current_user.id, deck_data, session)


@router.get("/", response_model=list[DeckResponse])
async def get_my_decks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_user_decks(current_user.id, session)


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_one(
    deck_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await get_deck(deck_id, session)


@router.patch("/{deck_id}", response_model=DeckResponse)
async def update(
    deck_id: UUID,
    deck_data: DeckUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await update_deck(deck_id, current_user.id, deck_data, session)


@router.delete("/{deck_id}")
async def delete(
    deck_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await delete_deck(deck_id, current_user.id, session)

