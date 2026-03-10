import pytest


@pytest.mark.asyncio
async def test_start_session(auth_client):
    # Create a deck with a card
    deck_response = await auth_client.post("/decks/", json={
        "title": "Study Deck",
        "description": "For studying",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    await auth_client.post("/cards/", json={
        "front": "Study question",
        "back": "Study answer",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })

    # Start session
    response = await auth_client.post("/study/sessions", json={
        "deck_id": deck_id,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["deck_id"] == deck_id
    assert data["total_reviewed"] == 0
    assert data["total_correct"] == 0


@pytest.mark.asyncio
async def test_start_session_empty_deck(auth_client):
    # Create empty deck
    deck_response = await auth_client.post("/decks/", json={
        "title": "Empty Deck",
        "description": "No cards",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    response = await auth_client.post("/study/sessions", json={
        "deck_id": deck_id,
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_submit_answer(auth_client):
    # Setup: deck, card, session
    deck_response = await auth_client.post("/decks/", json={
        "title": "Answer Deck",
        "description": "Test",
        "language": "python",
        "topic": "algorithms",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    card_response = await auth_client.post("/cards/", json={
        "front": "What is O(n)?",
        "back": "Linear time complexity",
        "card_type": "qa",
        "difficulty": 2,
        "ai_generated": False,
        "deck_id": deck_id,
    })
    card_id = card_response.json()["id"]

    session_response = await auth_client.post("/study/sessions", json={
        "deck_id": deck_id,
    })
    session_id = session_response.json()["id"]

    # Submit answer
    response = await auth_client.post(f"/study/sessions/{session_id}/answer", json={
        "card_id": card_id,
        "quality": 4,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert "next_review" in data
    assert "ease_factor" in data


@pytest.mark.asyncio
async def test_end_session(auth_client):
    # Setup
    deck_response = await auth_client.post("/decks/", json={
        "title": "End Session Deck",
        "description": "Test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    await auth_client.post("/cards/", json={
        "front": "Q",
        "back": "A",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })

    session_response = await auth_client.post("/study/sessions", json={
        "deck_id": deck_id,
    })
    session_id = session_response.json()["id"]

    # End session
    response = await auth_client.post(f"/study/sessions/{session_id}/end")
    assert response.status_code == 200
    data = response.json()
    assert data["completed_at"] is not None
