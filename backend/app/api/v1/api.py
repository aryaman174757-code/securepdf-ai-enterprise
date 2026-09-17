from fastapi import APIRouter
from app.api.v1 import auth, documents, tools, convert, ocr, chat, search, security, pipeline, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & IAM"])
api_router.include_router(documents.router, prefix="/documents", tags=["Zero-Trust Documents"])
api_router.include_router(tools.router, prefix="/tools", tags=["PDF Modification Tools"])
api_router.include_router(convert.router, prefix="/convert", tags=["Universal Conversion"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["Dual-Engine OCR"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Grounded RAG Chat"])
api_router.include_router(search.router, prefix="/search", tags=["Hybrid Search & Semantic"])
api_router.include_router(security.router, prefix="/security", tags=["Security Center & Cryptography"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Workflow Pipeline Builder"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin & Telemetry"])
