from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_deck(auth_client):
    response = await auth_client.post("/decks/", json={
        "title": "Test Deck",
        "description": "A test deck",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Deck"
    assert data["language"] == "python"
    assert data["is_public"] is False


@pytest.mark.asyncio
async def test_create_deck_unauthorized(client):
    response = await client.post("/decks/", json={
        "title": "Unauthorized Deck",
        "description": "Should fail",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_decks(auth_client):
    # Create a deck first
    await auth_client.post("/decks/", json={
        "title": f"Deck {uuid4().hex[:8]}",
        "description": "Test",
        "language": "python",
        "topic": "algorithms",
        "is_public": False,
    })

    response = await auth_client.get("/decks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_single_deck(auth_client):
    # Create a deck
    create_response = await auth_client.post("/decks/", json={
        "title": "Single Deck Test",
        "description": "Test",
        "language": "java",
        "topic": "backend",
        "is_public": True,
    })
    deck_id = create_response.json()["id"]

    response = await auth_client.get(f"/decks/{deck_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Deck Test"


@pytest.mark.asyncio
async def test_update_deck(auth_client):
    # Create a deck
    create_response = await auth_client.post("/decks/", json={
        "title": "Before Update",
        "description": "Test",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = create_response.json()["id"]

    # Update it
    response = await auth_client.patch(f"/decks/{deck_id}", json={
        "title": "After Update",
    })
    assert response.status_code == 200
    assert response.json()["title"] == "After Update"


@pytest.mark.asyncio
async def test_delete_deck(auth_client):
    # Create a deck
    create_response = await auth_client.post("/decks/", json={
        "title": "To Delete",
        "description": "Will be deleted",
        "language": "python",
        "topic": "general",
        "is_public": False,
    })
    deck_id = create_response.json()["id"]

    # Delete it
    response = await auth_client.delete(f"/decks/{deck_id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = await auth_client.get(f"/decks/{deck_id}")
    assert get_response.status_code == 404
