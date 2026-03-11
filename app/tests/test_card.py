from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_card(auth_client):
    # Create a deck first
    deck_response = await auth_client.post("/decks/", json={
        "title": "Card Test Deck",
        "description": "For testing cards",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    # Create a card
    response = await auth_client.post("/cards/", json={
        "front": "What is a variable?",
        "back": "A named container for storing data",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["front"] == "What is a variable?"
    assert data["deck_id"] == deck_id


@pytest.mark.asyncio
async def test_create_code_card(auth_client):
    deck_response = await auth_client.post("/decks/", json={
        "title": "Code Card Deck",
        "description": "For code cards",
        "language": "python",
        "topic": "algorithms",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    response = await auth_client.post("/cards/", json={
        "front": "Write a function to reverse a string",
        "back": "def reverse(s): return s[::-1]",
        "card_type": "code",
        "difficulty": 2,
        "code_template": "def reverse(s):\n    pass",
        "ai_generated": False,
        "deck_id": deck_id,
    })
    assert response.status_code == 200
    assert response.json()["card_type"] == "code"
    assert response.json()["code_template"] is not None


@pytest.mark.asyncio
async def test_get_deck_cards(auth_client):
    # Create deck and card
    deck_response = await auth_client.post("/decks/", json={
        "title": "Get Cards Deck",
        "description": "Test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    await auth_client.post("/cards/", json={
        "front": "Question 1",
        "back": "Answer 1",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })

    response = await auth_client.get(f"/cards/?deck_id={deck_id}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_update_card(auth_client):
    # Create deck and card
    deck_response = await auth_client.post("/decks/", json={
        "title": "Update Card Deck",
        "description": "Test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    card_response = await auth_client.post("/cards/", json={
        "front": "Original question",
        "back": "Original answer",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })
    card_id = card_response.json()["id"]

    # Update the card
    response = await auth_client.patch(f"/cards/{card_id}", json={
        "front": "Updated question",
    })
    assert response.status_code == 200
    assert response.json()["front"] == "Updated question"
    assert response.json()["back"] == "Original answer"  # unchanged


@pytest.mark.asyncio
async def test_delete_card(auth_client):
    deck_response = await auth_client.post("/decks/", json={
        "title": "Delete Card Deck",
        "description": "Test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    card_response = await auth_client.post("/cards/", json={
        "front": "To be deleted",
        "back": "Will be gone",
        "card_type": "qa",
        "difficulty": 1,
        "ai_generated": False,
        "deck_id": deck_id,
    })
    card_id = card_response.json()["id"]

    response = await auth_client.delete(f"/cards/{card_id}")
    assert response.status_code == 200

    get_response = await auth_client.get(f"/cards/{card_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_card_pagination(auth_client):
    # Create a deck
    deck_response = await auth_client.post("/decks/", json={
        "title": f"Pagination Deck {uuid4().hex[:8]}",
        "description": "For pagination test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = deck_response.json()["id"]

    # Create 3 cards
    for i in range(3):
        await auth_client.post("/cards/", json={
            "front": f"Question {i}",
            "back": f"Answer {i}",
            "card_type": "qa",
            "difficulty": 1,
            "ai_generated": False,
            "deck_id": deck_id,
        })

    # Request page 1 with per_page=2
    response = await auth_client.get(f"/cards/?deck_id={deck_id}&page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total_pages"] == 2

    # Request page 2
    response2 = await auth_client.get(f"/cards/?deck_id={deck_id}&page=2&per_page=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 1
    assert data2["page"] == 2
