from fastapi import APIRouter

router = APIRouter()


@router.get("/timeline")
async def timeline():
    return {"detail": "Not implemented yet"}


@router.get("/gaps")
async def gaps():
    return {"detail": "Not implemented yet"}


@router.get("/portfolio")
async def portfolio():
    return {"detail": "Not implemented yet"}
