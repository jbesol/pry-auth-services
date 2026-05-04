import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@email.com"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data


async def test_register_duplicate_email(client):
    # Registrar usuario por primera vez
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    # Intentar registrar con el mismo email
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "otrouser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


async def test_register_duplicate_username(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    response = await client.post("/api/v1/auth/register", json={
        "email": "otro@email.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@email.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@email.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


async def test_login_nonexistent_user(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "noexiste@email.com",
        "password": "password123"
    })
    assert response.status_code == 401


async def test_get_me_authenticated(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "test@email.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@email.com"


async def test_get_me_unauthenticated(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 403


async def test_logout(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@email.com",
        "username": "testuser",
        "password": "password123"
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "test@email.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Sesión cerrada correctamente"