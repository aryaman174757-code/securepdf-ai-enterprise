from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.db.models import User, Session, ApiKey, AuditLog
from app.core.security import SecurityManager, get_current_user_token
from app.schemas.all_schemas import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    UserResponse, ApiKeyCreate, ApiKeyResponse
)

router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def signup(payload: UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    # Check existing user
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = SecurityManager.hash_password(payload.password)
    user = User(
        email=payload.email,
        hashed_password=hashed_pw,
        full_name=payload.full_name,
        role="user",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.flush()

    # Fingerprint & Session
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown")
    dfp = SecurityManager.compute_device_fingerprint(user_agent, client_ip)

    access_token = SecurityManager.create_access_token(subject=user.id, role=user.role, device_fingerprint=dfp)
    refresh_token = SecurityManager.create_refresh_token(subject=user.id, device_fingerprint=dfp)
    token_claims = SecurityManager.decode_token(access_token)

    db_session = Session(
        user_id=user.id,
        token_jti=token_claims["jti"],
        device_fingerprint=dfp,
        user_agent=user_agent,
        ip_address=client_ip,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600 * 2,
        user_id=user.id,
        email=user.email,
        role=user.role,
        is_pro=user.is_pro
    )

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not SecurityManager.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown")
    dfp = SecurityManager.compute_device_fingerprint(user_agent, client_ip)

    access_token = SecurityManager.create_access_token(subject=user.id, role=user.role, device_fingerprint=dfp)
    refresh_token = SecurityManager.create_refresh_token(subject=user.id, device_fingerprint=dfp)
    token_claims = SecurityManager.decode_token(access_token)

    db_session = Session(
        user_id=user.id,
        token_jti=token_claims["jti"],
        device_fingerprint=dfp,
        user_agent=user_agent,
        ip_address=client_ip,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_session)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        ip_address=client_ip,
        user_agent=user_agent,
        resource_type="auth",
        metadata_json={"email": user.email}
    )
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600 * 2,
        user_id=user.id,
        email=user.email,
        role=user.role,
        is_pro=user.is_pro
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == token_data["sub"])
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_user_api_key(
    payload: ApiKeyCreate,
    token_data: Dict[str, Any] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = token_data["sub"]
    raw_key, key_hash = SecurityManager.generate_api_key()
    
    api_key_record = ApiKey(
        user_id=user_id,
        name=payload.name,
        key_prefix=raw_key[:12],
        key_hash=key_hash,
        is_active=True
    )
    db.add(api_key_record)
    await db.commit()
    await db.refresh(api_key_record)

    return ApiKeyResponse(
        id=api_key_record.id,
        name=api_key_record.name,
        key_prefix=api_key_record.key_prefix,
        raw_api_key=raw_key,
        is_active=api_key_record.is_active,
        created_at=api_key_record.created_at
    )
