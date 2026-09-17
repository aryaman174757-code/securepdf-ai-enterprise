import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union, Tuple
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

# Argon2 Password Hashing Context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4
)

security_scheme = HTTPBearer(auto_error=False)

class SecurityManager:
    """Enterprise Security Manager: Passwords, JWT Tokens, API Keys, Sessions"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash plaintext password using Argon2id with memory hardness."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plaintext against Argon2id hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        subject: Union[str, int],
        role: str = "user",
        tenant_id: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create signed JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload: Dict[str, Any] = {
            "sub": str(subject),
            "role": role,
            "tenant_id": tenant_id or "default",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_hex(16),
            "dfp": device_fingerprint or "unknown"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(subject: Union[str, int], device_fingerprint: Optional[str] = None) -> str:
        """Create signed long-lived refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload: Dict[str, Any] = {
            "sub": str(subject),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_hex(24),
            "dfp": device_fingerprint or "unknown"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token claims."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    @staticmethod
    def generate_api_key(prefix: str = "spdf_live_") -> Tuple[str, str]:
        """
        Generates a secure API key.
        Returns: (raw_api_key, sha256_hashed_key)
        """
        raw_token = secrets.token_urlsafe(32)
        full_key = f"{prefix}{raw_token}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        return full_key, key_hash

    @staticmethod
    def compute_device_fingerprint(user_agent: str, client_ip: str) -> str:
        """Computes a persistent device fingerprint hash."""
        raw = f"{user_agent}:{client_ip}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


async def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """Dependency extracting and verifying the bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return SecurityManager.decode_token(credentials.credentials)


async def require_admin(token_data: Dict[str, Any] = Depends(get_current_user_token)) -> Dict[str, Any]:
    """Dependency verifying administrative privileges."""
    if token_data.get("role") not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return token_data
