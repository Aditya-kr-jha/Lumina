from datetime import timedelta

from fastapi import FastAPI, HTTPException, Depends
import uvicorn
import logging
from contextlib import asynccontextmanager

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from app.routes.api import api_router
from app.db.session import create_db_and_tables_async, get_async_session
from app.auth import authenticate_user, create_access_token
from app.config import settings
from app.models.schemas import Token

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the FastAPI application...")
    # Now we can directly call the async function without threadpool
    await create_db_and_tables_async()
    yield
    print("Shutting down the FastAPI application...")


# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Intelligent PDF Chat Assistant API",
    description="Backend API for RAG-based PDF question answering",
    version="1.0.0",
)
app.include_router(api_router, prefix="/api/v1")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5176",
    "http://localhost:5174",
    "http://localhost:5177",
    "http://localhost:5175",
    "https://dg9qzy1dkyjl5.cloudfront.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent PDF Chat Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoints"""
    return {
        "status": "healthy",
    }


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    """Handles user login and returns JWT access token."""
    # We can directly await the async authentication function
    user = await authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
