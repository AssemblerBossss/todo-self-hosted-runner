import secrets
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError

from app.config import settings
from logging import getLogger

logger = getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT Access Token"""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "sub": str(data["user_id"]),
            "email": data["email"],
            "role": data["role"],
            "is_active": data.get("is_active", True),
            "token_type": "access",
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token() -> str:
    """Создает случайный Refresh Token"""
    return secrets.token_urlsafe(48)


def verify_access_token(token: str) -> dict | None:
    """
    Проверяет JWT токен и возвращает payload если токен валидный

    Args:
        token: JWT токен для проверки

    Returns:
        dict: payload токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if not payload.get("user_id"):
            logger.error("Token missing user_id")
            return None
        return payload

    except ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except JWTError as e:
        logger.error("Invalid token: %s", e)
        return None


def extract_bearer_token(authorization_header: str | None) -> str | None:
    """
    Извлекает JWT токен из заголовка Authorization.

    Ожидаемый формат: "Bearer <token>"

    Args:
        authorization_header: значение заголовка Authorization

    Returns:
        Токен или None, если заголовок отсутствует или имеет неверный формат
    """
    if authorization_header is None:
        logger.error("Auth Middleware: authorization_header is None")
        return None

    parts = authorization_header.strip().split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.error("Auth Middleware: authorization_header is not Bearer")
        return None
    return parts[1]
