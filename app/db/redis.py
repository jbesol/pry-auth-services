#Database guarda datos en RAM, es rápido pero volátil (se pierden al reiniciar el servidor). Es ideal para almacenar datos temporales como sesiones, caché o tokens de acceso.

import redis.asyncio as aioredis

from app.core.model_config import settings

# Pool de conexiones a Redis
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,  # Retorna strings en lugar de bytes
)


async def get_redis() -> aioredis.Redis:
    return redis_client