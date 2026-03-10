from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_signup_success(client):
    response = await client.post("/user/signup", json={
        "username": f"newuser_{uuid4().hex[:8]}",
        "email": f"new_{uuid4().hex[:8]}@test.com",
        "password": "securepassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    email = f"dup_{uuid4().hex[:8]}@test.com"
    user_data = {
        "username": f"user1_{uuid4().hex[:8]}",
        "email": email,
        "password": "password123",
    }
    await client.post("/user/signup", json=user_data)

    # Try to sign up again with same email
    user_data["username"] = f"user2_{uuid4().hex[:8]}"
    response = await client.post("/user/signup", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client):
    email = f"login_{uuid4().hex[:8]}@test.com"
    await client.post("/user/signup", json={
        "username": f"loginuser_{uuid4().hex[:8]}",
        "email": email,
        "password": "password123",
    })

    response = await client.post("/user/login", data={
        "username": email,
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = f"wrong_{uuid4().hex[:8]}@test.com"
    await client.post("/user/signup", json={
        "username": f"wronguser_{uuid4().hex[:8]}",
        "email": email,
        "password": "password123",
    })

    response = await client.post("/user/login", data={
        "username": email,
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(auth_client):
    response = await auth_client.get("/user/me")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/user/me")
    assert response.status_code == 401
