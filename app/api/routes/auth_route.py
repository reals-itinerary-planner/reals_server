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
) -> ResponseSchema[any]:

    controller = AuthController(db)
    result = await controller.login(email, password)
    return ResponseSchema.success(result=result, message="Login successful")
