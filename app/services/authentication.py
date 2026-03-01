import hashlib
import hmac
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, TypedDict
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class RefreshTokenBundle(TypedDict):
    token: str
    jti: str
    family_id: str
    expires_at: datetime


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using HMAC with SHA-256."""
    return hmac.new(
        key=settings.REFRESH_TOKEN_PEPPER.encode("utf-8"),
        msg=token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def create_refresh_token(subject: str, family_id: str) -> RefreshTokenBundle:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid4())

    payload: Dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "jti": jti,
        "fid": family_id,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return {
        "token": token,
        "jti": jti,
        "family_id": family_id,
        "expires_at": expires_at,
    }


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """Create a JWT token."""
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    """Create an access token."""
    return _create_token(
        subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str, token_type: str) -> Dict[str, Any]:
    """Decode a JWT token and validate its claims."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except JWTError as e:
        raise JWTError(f"Invalid {token_type} token: {str(e)}") from e
