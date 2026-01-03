import pytest


def register(client, email="watch@test.com", password="watchpassword"):
    r = client.post("/v1/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 201)


def login_and_token(client, email="watch@test.com", password="watchpassword") -> str:
    r = client.post("/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    data = r.json()
    # your API returns {"status":"ok","access_token": "...", "token_type":"bearer"}
    return data["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_watchlist_requires_auth(client):
    r = client.get("/v1/watchlists/")
    assert r.status_code == 401


def test_add_list_update_delete_watchlist_flow(client):
    # register + login
    register(client)
    token = login_and_token(client)
    headers = auth_headers(token)

    # add item (should be 201 now)
    r = client.post("/v1/watchlists/items", json={"title": "Test Movie", "type": "movie"}, headers=headers)
    assert r.status_code == 201
    item_id = r.json()["item"]["id"]

    # list should include it
    r = client.get("/v1/watchlists/?skip=0&limit=10", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert any(i["id"] == item_id for i in data["watchlist"])

    # update title
    r = client.patch(f"/v1/watchlists/items/{item_id}", json={"title": "Updated Movie"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["item"]["title"] == "Updated Movie"

    # filter should work
    r = client.get("/v1/watchlists/?type=movie&sort=created_at_desc", headers=headers)
    assert r.status_code == 200
    assert all(i["type"] == "movie" for i in r.json()["watchlist"])

    # delete should be 204 now
    r = client.delete(f"/v1/watchlists/items/{item_id}", headers=headers)
    assert r.status_code == 204

    # list should no longer include it
    r = client.get("/v1/watchlists/?skip=0&limit=50", headers=headers)
    assert r.status_code == 200
    assert all(i["id"] != item_id for i in r.json()["watchlist"])
