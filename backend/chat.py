from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat():
    return {"detail": "Not implemented yet"}
