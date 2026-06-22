import httpx
from auth.config import (
    FRONTEND_CALLBACK_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)
from auth.dependencies import get_current_user
from auth.encryption import encrypt
from auth.jwt import create_access_token
from database.database import get_db
from database.models import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = " ".join(
    [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
)


@router.get("/login")
async def login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",  # refresh_token 받기 위해
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/callback")
async def callback(code: str, db: AsyncSession = Depends(get_db)):
    # 1. code → token 교환
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_res.json()

        # 2. userinfo 조회
        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        userinfo = userinfo_res.json()

    # 3. DB upsert
    result = await db.execute(select(User).where(User.id == userinfo["sub"]))
    user = result.scalar_one_or_none()

    if user:
        user.access_token = encrypt(token_data["access_token"])
        if "refresh_token" in token_data:
            user.refresh_token = encrypt(token_data["refresh_token"])
    else:
        user = User(
            id=userinfo["sub"],
            email=userinfo["email"],
            name=userinfo["name"],
            picture=userinfo.get("picture"),
            access_token=encrypt(token_data["access_token"]),
            refresh_token=(
                encrypt(token_data["refresh_token"])
                if "refresh_token" in token_data
                else None
            ),
        )
        db.add(user)

    await db.commit()

    # 4. 자체 JWT 발급 → Streamlit으로 redirect
    jwt_token = create_access_token({"sub": user.id, "email": user.email})
    return RedirectResponse(f"{FRONTEND_CALLBACK_URL}?token={jwt_token}")


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
    }


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    return {"message": "logged out"}
