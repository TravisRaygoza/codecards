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
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1


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


@pytest.mark.asyncio
async def test_deck_pagination(auth_client):
    # Create 3 decks
    for i in range(3):
        await auth_client.post("/decks/", json={
            "title": f"Page Deck {uuid4().hex[:8]}",
            "description": "Pagination test",
            "language": "python",
            "topic": "general",
            "is_public": False,
        })

    # Request page 1 with per_page=2
    response = await auth_client.get("/decks/?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] >= 3
    assert data["total_pages"] >= 2

    # Request page 2
    response2 = await auth_client.get("/decks/?page=2&per_page=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) >= 1
    assert data2["page"] == 2
