
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from sqlmodel import select

from app.api.schemas.card import CardCreate, CardUpdate
from app.database.models import Card



async def create_card(deck_id: UUID, card_data: CardCreate, session: AsyncSession):
    new_card = Card(
        deck_id=deck_id,
        front=card_data.front,
        back=card_data.back,
        card_type=card_data.card_type,
        difficulty=card_data.difficulty,
        code_template=card_data.code_template,
        ai_generated=card_data.ai_generated,
    )

    session.add(new_card)
    await session.commit()
    await session.refresh(new_card)

    return new_card

async def get_deck_cards(deck_id: UUID, session: AsyncSession):
    statement = select(Card).where(Card.deck_id == deck_id)
    result = await session.execute(statement)
    cards = result.scalars().all()


    return cards

async def get_card(card_id: UUID, session: AsyncSession):
    statement = select(Card).where(Card.id == card_id)
    result = await session.execute(statement)
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail="card not found")
    
    return card

async def update_card(card_id: UUID, card_data: CardUpdate, session: AsyncSession):

    card = await get_card(card_id, session)
    
    update_data = card_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(card, key, value)

    
    session.add(card)
    await session.commit()
    await session.refresh(card)

    return card 

async def delete_card(card_id: UUID, session: AsyncSession):
    card = await get_card(card_id, session)

    
    await session.delete(card)
    await session.commit()

    return {"detail": "Card deleted"}