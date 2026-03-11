from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas.card import CardCreate, CardResponse, CardUpdate
from app.api.schemas.pagination import PaginatedResponse
from app.database.models import User
from app.database.session import get_session
from app.services.card import (
    create_card,
    delete_card,
    get_card,
    get_deck_cards,
    update_card,
)


router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("/", response_model=CardResponse)
async def create(
    card_data: CardCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await create_card(card_data.deck_id, card_data, session)


@router.get("/", response_model=PaginatedResponse[CardResponse])
async def get_my_cards(
    deck_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    return await get_deck_cards(deck_id, session, page, per_page)


@router.get("/{card_id}", response_model=CardResponse)
async def get_one(card_id: UUID, session: AsyncSession = Depends(get_session)):
    return await get_card(card_id, session)


@router.patch("/{card_id}", response_model=CardResponse)
async def update(
    card_id: UUID,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await update_card(card_id, card_data, session)


@router.delete("/{card_id}")
async def delete(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await delete_card(card_id, session)
