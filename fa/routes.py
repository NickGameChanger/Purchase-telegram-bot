from fastapi import APIRouter
from fa.banks import router

api_router = APIRouter()

api_router.include_router(router)
