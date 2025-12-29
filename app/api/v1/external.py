from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/ping")
async def ping_external():
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get("https://httpbin.org/get")
        return {"status_code": r.status_code, "data": r.json()}