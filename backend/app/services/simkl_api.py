import httpx, os

from app.loggers import debug_logger

API_SECRET_KEY = os.environ.get("SIMKL_API_SECRET_KEY")
BASE_URL = "https://api.simkl.com"

get_category_path = {1: "movie",
                     2: "anime",
                     3: "tv"}

async def search_simkl_media(category_id: int, query: str):
    media_type = get_category_path[category_id]
    url = f"{BASE_URL}/search/{media_type}"
    params = {
        "q": query,
        "page": 1,
        "limit": 10,
        "client_id": API_SECRET_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []


async def get_simkl_media_details(simkl_id: int):
    url = f"{BASE_URL}/search/id"
    params = {
        "simkl": simkl_id,
        "client_id": API_SECRET_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            debug_logger.warning(response.json())
            return response.json()
        return []