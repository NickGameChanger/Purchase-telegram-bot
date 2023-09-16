from fastapi import APIRouter
from typing import Any
router = APIRouter()


@router.get('/vakif')
async def root() -> Any:
    return {"message": "Hello World"}