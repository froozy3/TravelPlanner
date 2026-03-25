import httpx
from fastapi import HTTPException
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)


class ArtInstituteClient:
    BASE_URL = "https://api.artic.edu/api/v1/artworks"

    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=600)

    async def validate_place(self, external_id: int) -> bool:
        if external_id in self.cache:
            return self.cache[external_id]

        url = f"{self.BASE_URL}/{external_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                print(f"Response: {response.json()}")
                if response.status_code == 200:
                    self.cache[external_id] = True
                    return True
                if response.status_code == 404:
                    self.cache[external_id] = False
                    return False

                response.raise_for_status()

            except httpx.HTTPError as e:
                logger.error(f"Error connecting to Art Institute API: {e}")
                raise HTTPException(status_code=502, detail="External API unavailable")

        return False


art_client = ArtInstituteClient()
