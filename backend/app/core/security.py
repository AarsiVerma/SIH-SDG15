"""Password hashing and JWT utilities."""
import bcrypt

from app.core.config import get_settings


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    import time
    import jwt

    settings = get_settings()
    to_encode = data.copy()
    expire = int(time.time()) + (expires_delta or settings.jwt_expire_minutes * 60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    import jwt
    from app.core.errors import AppError, ErrorCode

    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise AppError(ErrorCode.TOKEN_EXPIRED)
    except jwt.InvalidTokenError:
        raise AppError(ErrorCode.INVALID_TOKEN)