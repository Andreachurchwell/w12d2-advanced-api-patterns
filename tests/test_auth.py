import pytest
import httpx
from uuid import uuid4

from app.main import app


@pytest.mark.asyncio
async def test_register_login_and_me():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "strongpassword"

        # register
        r = await ac.post(
            "/v1/auth/register",
            json={"email": email, "password": password},
        )
        assert r.status_code == 200

        # login
        r = await ac.post(
            "/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert r.status_code == 200

        data = r.json()
        assert data.get("status") == "ok"
        assert "access_token" in data
        token = data["access_token"]

        # me
        r = await ac.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == email.lower()