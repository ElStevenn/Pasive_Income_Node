from fastapi import APIRouter, Depends, HTTPException
from typing import Literal, List
import docker

router = APIRouter(
    prefix="/economic_calendar",
    tags=["Economic Calendar"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
async def get_status():
    return {"response", "under construction"}

