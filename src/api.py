from fastapi import APIRouter

from src.auth import auth_router
from src.config import get_settings
from src.travel import travel_router, places_router

settings = get_settings()
api_v1 = APIRouter(prefix=settings.API_V1_PREFIX)

api_v1.include_router(travel_router)
api_v1.include_router(places_router)

api_v1.include_router(auth_router)