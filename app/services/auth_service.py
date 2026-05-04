from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.model_config import settings


# --- Excepciones personalizadas ---

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


# --- Servicio ---

async def register_user(data: UserRegister, db: AsyncSession) -> UserResponse:
    # Verificar si el email ya existe
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise AuthError("El email ya está registrado", status_code=400)

    # Verificar si el username ya existe
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise AuthError("El username ya está en uso", status_code=400)

    # Crear usuario
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()  # Obtiene el ID sin hacer commit todavía

    return UserResponse.model_validate(user)


async def login_user(data: UserLogin, db: AsyncSession) -> TokenResponse:
    # Buscar usuario por email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Mismo error si no existe o si la contraseña es incorrecta
    # Esto evita que un atacante sepa si el email existe o no
    if not user or not verify_password(data.password, user.hashed_password):
        raise AuthError("Credenciales inválidas", status_code=401)

    if not user.is_active:
        raise AuthError("Cuenta inactiva", status_code=403)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def logout_user(token: str, redis: aioredis.Redis) -> None:
    payload = decode_token(token)
    if not payload:
        raise AuthError("Token inválido", status_code=401)

    # Guardar token en blacklist con TTL igual al tiempo restante de expiración
    import time
    ttl = int(payload["exp"] - time.time())
    if ttl > 0:
        await redis.setex(f"blacklist:{token}", ttl, "revoked")


async def refresh_tokens(refresh_token: str, redis: aioredis.Redis) -> TokenResponse:
    payload = decode_token(refresh_token)

    if not payload:
        raise AuthError("Token inválido", status_code=401)

    if payload.get("type") != "refresh":
        raise AuthError("Token inválido", status_code=401)

    # Verificar que no esté en blacklist
    is_blacklisted = await redis.get(f"blacklist:{refresh_token}")
    if is_blacklisted:
        raise AuthError("Token revocado", status_code=401)

    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})

    # Revocar el refresh token usado — cada refresh token es de un solo uso
    await redis.setex(f"blacklist:{refresh_token}", settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, "revoked")

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )