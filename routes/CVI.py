from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix="/cvi",
    tags=["CVI"],
    responses={404: {"description": "Not found"}},
)



@router.get("/")
async def see_status():
    return {"response": "under response"}

@router.post("/suscribe")
async def suscribe():
    return {"response": "under response"}

@router.post("/status/{new_status}")
async def status(new_status: str):
    return {"response": "under response"}

@router.post("/conf")
async def set_conf():
    return {"response": "under response"}

@router.get("/conf")
async def view_conf():
    return {"response": "under response"}

@router.get("/get_historical")
async def get_historical_cvi():
    return {"response": "under response"}
