def test_me_requires_token(client):
    r = client.get("/v1/auth/me")
    assert r.status_code == 401


def test_register_login_and_me(client):
    r = client.post("/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert r.status_code == 200

    r = client.post("/v1/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert r.status_code == 200
    print("LOGIN JSON:", r.json())

    token = r.json()["access_token"]

    r = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"