from fastapi import APIRouter, Query
from app.services.search_service import search_documents
from app.core.redis import get_cached, set_cached

router = APIRouter()

@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    cache_key = f"search:{q}:{page}:{size}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    results = await search_documents(q, page, size)
    response = {
        "query": q,
        "page": page,
        "size": size,
        "total": len(results),
        "results": results
    }
    await set_cached(cache_key, response, expire=300)
    return response