from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/github")
async def github_status():
    # Simple external call to prove async httpx usage
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get("https://api.github.com")
        r.raise_for_status()
        data = r.json()

    # Return a small, stable subset
    return {
        "github_api_status": "ok",
        "current_user_url": data.get("current_user_url"),
        "rate_limit_url": data.get("rate_limit_url"),
    }