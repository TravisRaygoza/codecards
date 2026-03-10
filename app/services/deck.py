from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.schemas.deck import DeckCreate, DeckUpdate
from app.database.models import Deck
from app.database.redis import cache_delete, cache_delete_pattern, cache_get, cache_set


async def create_deck(user_id: UUID, deck_data: DeckCreate, session: AsyncSession):
    new_deck = Deck(
        title=deck_data.title,
        description=deck_data.description,
        language=deck_data.language,
        topic=deck_data.topic,
        is_public=deck_data.is_public,
        user_id=user_id,
    )

    session.add(new_deck)
    await session.commit()
    await session.refresh(new_deck)

    # Clear the user's deck list cache (it's now outdated)
    await cache_delete(f"user_decks:{user_id}")

    return new_deck


async def get_user_decks(user_id: UUID, session: AsyncSession):
    # Check cache first
    cache_key = f"user_decks:{user_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    # Not in cache, query database
    statement = select(Deck).where(Deck.user_id == user_id)
    result = await session.execute(statement)
    decks = result.scalars().all()

    # Store in cache for next time
    decks_data = [
        {
            "id": str(d.id),
            "user_id": str(d.user_id),
            "title": d.title,
            "description": d.description,
            "language": d.language.value if d.language else None,
            "topic": d.topic.value,
            "is_public": d.is_public,
            "created_at": str(d.created_at),
        }
        for d in decks
    ]
    await cache_set(cache_key, decks_data)

    return decks


async def get_deck(deck_id: UUID, session: AsyncSession):
    # Check cache first
    cache_key = f"deck:{deck_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    statement = select(Deck).where(Deck.id == deck_id)
    result = await session.execute(statement)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    # Store in cache
    deck_data = {
        "id": str(deck.id),
        "user_id": str(deck.user_id),
        "title": deck.title,
        "description": deck.description,
        "language": deck.language.value if deck.language else None,
        "topic": deck.topic.value,
        "is_public": deck.is_public,
        "created_at": str(deck.created_at),
    }
    await cache_set(cache_key, deck_data)

    return deck


async def update_deck(deck_id: UUID, user_id: UUID, deck_data: DeckUpdate, session: AsyncSession):
    deck = await get_deck(deck_id, session)

    if isinstance(deck, dict):
        # Cache returned a dict, need the actual DB object
        statement = select(Deck).where(Deck.id == deck_id)
        result = await session.execute(statement)
        deck = result.scalar_one_or_none()

    if deck.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your deck")

    update_data = deck_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deck, key, value)

    session.add(deck)
    await session.commit()
    await session.refresh(deck)

    # Clear cache (data changed)
    await cache_delete(f"deck:{deck_id}")
    await cache_delete(f"user_decks:{user_id}")

    return deck


async def delete_deck(deck_id: UUID, user_id: UUID, session: AsyncSession):
    deck = await get_deck(deck_id, session)

    if isinstance(deck, dict):
        statement = select(Deck).where(Deck.id == deck_id)
        result = await session.execute(statement)
        deck = result.scalar_one_or_none()

    if deck.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your deck")

    await session.delete(deck)
    await session.commit()

    # Clear cache
    await cache_delete(f"deck:{deck_id}")
    await cache_delete(f"user_decks:{user_id}")

    return {"detail": "Deck deleted"}
