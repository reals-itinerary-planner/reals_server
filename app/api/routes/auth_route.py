from fastapi import APIRouter, Body, Depends, Query, HTTPException
from app.core.database import get_async_db
from app.controllers.auth_controller import AuthController
from sqlalchemy.ext.asyncio import AsyncSession
from ...schemas.response_schema import ResponseSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    email: str = Body(..., description="Email"),
    password: str = Body(..., description="Password"),
    db: AsyncSession = Depends(get_async_db),
):

    controller = AuthController(db)
    result = await controller.login(email, password)
    return result


@router.post("/register")
async def register(
    email: str = Body(..., description="Email"),
    password: str = Body(..., description="Password"),
    username: str = Body(..., description="Username"),
    db: AsyncSession = Depends(get_async_db),
):
    controller = AuthController(db)
    result = await controller.register(email, password, username)
    return result
