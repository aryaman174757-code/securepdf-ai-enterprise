from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import init_db
from app.api.v1.api import api_router
from app.websockets.manager import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Schemas
    await init_db()
    yield
    # Shutdown: Clean up any ephemeral handles if needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise Zero-Trust AI Document Intelligence, Cryptography & Workflow Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# WebSocket Live Event Gateway
@app.websocket("/ws/live/{user_id}")
async def websocket_live_endpoint(websocket: WebSocket, user_id: str):
    await ws_manager.connect_user(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping-pong or handle client subscriptions
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect_user(websocket, user_id)

# Health & Readiness
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "zero_trust_status": "ENFORCED"
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "SecurePDF AI Enterprise Core API v3.0",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

# Mount API v1
app.include_router(api_router, prefix=settings.API_V1_STR)
