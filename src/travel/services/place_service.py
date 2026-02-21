import httpx
from fastapi import HTTPException, status

from src.config import get_settings

setting = get_settings()

async def validate_external_place(external_id: str) -> bool:
    """
    Checks if the artwork exists in the Art Institute of Chicago API.
    """
    async with httpx.AsyncClient() as client:
        print(f"{setting.ART_INSTITUTE_API_URL}/{external_id}")
        try:
            response = await client.get(
                f"{setting.ART_INSTITUTE_API_URL}/{external_id}"
            )
            if response.status_code == 200:
                return True
            return False
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Third-party API is currently unavailable"
            )