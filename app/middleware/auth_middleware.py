from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Optional
from jose import jwt
from app.models.user_model import User
from app.repositories.base_repository import BaseRepository
from ..core.config import settings
from app.core.database import async_session_maker

security = HTTPBearer()

# Define paths that don't need authentication
PUBLIC_PATHS = {
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/docs",  # Swagger UI
    "/redoc",  # ReDoc UI
    "/openapi.json",  # OpenAPI schema
}


def is_public_path(path: str) -> bool:
    """Check if path is public"""
    return any(path.startswith(public_path) for public_path in PUBLIC_PATHS)


async def verify_token(
    credentials: HTTPAuthorizationCredentials, db: AsyncSession
) -> Optional[dict]:
    """Verify JWT token and return user data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        # Get user from database to verify they still exist and are active
        user_repo = BaseRepository(User, db)
        user = await user_repo.get_first(
            filters={"filter_by[uuid][equals]": payload.get("sub")},
            include=["login_sessions"],
        )

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        if user.login_sessions.token != token:
            raise HTTPException(status_code=401, detail="Token has been revoked")

        print("payload is", payload)
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=401, detail="Authentication failed")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """Middleware to verify authentication token"""
        # Create new database session for each request
        async with async_session_maker() as session:
            # Add session to request state
            request.state.db = session

            try:
                # Skip auth for public paths
                if is_public_path(request.url.path):
                    response = await call_next(request)
                    return response

                # Get token from header
                try:
                    credentials = await security(request)
                except HTTPException:
                    # return JSONResponse(
                    #     status_code=401,
                    #     content={"detail": "Missing or invalid authentication token"},
                    # )
                    raise HTTPException(
                        status_code=401,
                        detail="Missing or invalid authentication token",
                    )

                try:
                    # Verify token
                    payload = await verify_token(credentials, session)
                    print("payload is", payload)
                    # Add user data to request state
                    request.state.user = payload
                    print("request.state.user is", request.state.user)
                    # Continue processing the request
                    response = await call_next(request)
                    print("response is", response)
                    return response

                except HTTPException as e:
                    print("HTTPException: ", e)
                    # return JSONResponse(
                    #     status_code=401, content={"detail": str(e.detail)}
                    # )
                    raise HTTPException(status_code=401, detail=str(e.detail))

            except Exception as e:
                print("Authentication failed: ", e)
                # return JSONResponse(
                #     status_code=401, content={"detail": "Authentication failed"}
                # )
                raise HTTPException(status_code=401, detail="Authentication failed")
            finally:
                # Close the database session
                await session.close()
