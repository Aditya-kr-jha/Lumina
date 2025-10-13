from fastapi import APIRouter
from app.routes import chat, document
from app.routes import users

# Create main API router
api_router = APIRouter()

api_router.include_router(users.router, prefix="/user", tags=["users"])
# Include sub-routers with prefixes and tags
api_router.include_router(document.router, prefix="/documents", tags=["documents"])

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
