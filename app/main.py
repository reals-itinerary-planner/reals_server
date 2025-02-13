from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .middleware.auth_middleware import (
    AuthMiddleware,
)  # Import the class, not the module
from .middleware.response_middleware import ResponseMiddleware

from app.api.routes import router as api_router
import uvicorn

from app.core.database import init_db
from app.middleware.rate_limiter import rate_limit_middleware
from dist.packages.starlette.middleware.cors import CORSMiddleware
from app.middleware import auth_middleware
from .schemas.response_schema import ResponseSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

# # Add rate limiter middleware
# app.middleware("http")(rate_limit_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add response middleware before auth middleware
app.add_middleware(ResponseMiddleware)

# Add authentication middleware
app.add_middleware(AuthMiddleware)
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseSchema.error(
            status_code=exc.status_code, message=str(exc.detail)
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseSchema.error(status_code=500, message=str(exc)).dict(),
    )


# Add this if you want to run the server directly from this file
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Accepts connections from all IPs
        port=8000,  # Port number
        reload=True,  # Auto-reload on code changes
    )
