from fastapi import APIRouter, Depends, HTTPException
from services.economic_calendar.economic_calendar_service import EconomicCalendarData
from typing import Literal, List
import docker

router = APIRouter(
    prefix="/economic_calendar",
    tags=["Economic Calendar"],
    responses={404: {"description": "Not found"}},
)

economic_calendar_servixe = EconomicCalendarData()

@router.get("")
async def get_status():
    

    return {"response", "under construction"}

@router.post("/get_notified/{user_id}/{level}")
async def get_notified():
    pass

@router.post("/create_alert/{user_id}/{event_name}")
async def create_alert():
    return

@router.get("/check_event", description="Check if today there is an important event")
async def check_if_today_there_is_any_event():
    return {"response": "under construction"}
