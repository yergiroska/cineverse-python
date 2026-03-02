"""
Configuración de Redis para caché
"""
import redis
from typing import Optional

# Configuración de Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Cliente Redis global
_redis_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    """
    Obtiene la instancia de Redis.
    Retorna None si Redis no está disponible.
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Verificar conexión
            _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            print("⚠️  Redis no disponible - continuando sin caché")
            _redis_client = None

    return _redis_client


def clear_cache(pattern: str = "*"):
    """
    Limpia el caché que coincida con el patrón.

    Args:
        pattern: Patrón de keys a eliminar (default: todas)
    """
    client = get_redis()
    if client:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)