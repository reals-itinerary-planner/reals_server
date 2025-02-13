from http.client import HTTPException
from fastapi import Depends
from app.core.database import get_async_db
from app.repositories.base_repository import BaseRepository
from app.service.auth_service import AuthService
from dist.packages.sqlalchemy.ext.asyncio.session import AsyncSession


class AuthController:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

        self.auth_service = AuthService(self.db)

    async def login(self, email: str, password: str):
        user = await self.auth_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = await self.auth_service.create_token(user)
        return {"jwt": token, "token_type": "Bearer"}

    async def refresh_token(self, token: str):
        new_token = await self.auth_service.verify_token(token)
        if not new_token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        # token = await self.auth_service.create_token(user)
        return {"jwt": new_token, "token_type": "Bearer"}

    async def logout(self, user_id: str):
        # await self.auth_service.logout(user_id)
        return {"message": "Logged out successfully"}
