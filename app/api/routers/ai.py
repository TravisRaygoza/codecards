from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas.ai import GenerateCardsRequest, GeneratedCard
from app.api.schemas.card import CardResponse
from app.database.models import Card, User
from app.database.session import get_session
from app.services.ai import generate_cards

router = APIRouter(prefix="/ai", tags=["AI Generation"])


@router.post("/generate", response_model=list[GeneratedCard])
async def generate(
    request: GenerateCardsRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate flashcards using AI. Returns cards without saving them."""
    return await generate_cards(request)


@router.post("/generate-and-save/{deck_id}", response_model=list[CardResponse])
async def generate_and_save(
    deck_id: UUID,
    request: GenerateCardsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate flashcards using AI and save them directly to a deck."""
    generated = await generate_cards(request)

    saved_cards = []
    for card_data in generated:
        new_card = Card(
            deck_id=deck_id,
            front=card_data.front,
            back=card_data.back,
            card_type=request.card_type,
            difficulty=card_data.difficulty,
            code_template=card_data.code_template,
            ai_generated=True,
        )
        session.add(new_card)
        saved_cards.append(new_card)

    await session.commit()

    for card in saved_cards:
        await session.refresh(card)

    return saved_cards
