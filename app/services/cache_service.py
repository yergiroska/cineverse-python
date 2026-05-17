"""
Servicio de Cache con Redis para optimizar requests a TMDB API
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from app.config import settings


class CacheService:
    """Servicio para manejar cache con Redis"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1 hora en segundos

    async def connect(self):
        """Conectar a Redis"""
        try:
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            # Verificar conexión
            await self.redis_client.ping()
            print("✅ Conectado a Redis exitosamente")
        except Exception as e:
            print(f"⚠️ No se pudo conectar a Redis: {e}")
            self.redis_client = None

    async def disconnect(self):
        """Desconectar de Redis"""
        if self.redis_client:
            await self.redis_client.close()
            print("❌ Desconectado de Redis")

    async def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del cache

        Args:
            key: Clave del cache

        Returns:
            Valor deserializado o None si no existe
        """
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error al obtener del cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Guardar valor en el cache

        Args:
            key: Clave del cache
            value: Valor a guardar (será serializado a JSON)
            ttl: Tiempo de vida en segundos (default: 1 hora)

        Returns:
            True si se guardó exitosamente
        """
        if not self.redis_client:
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"Error al guardar en cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Eliminar valor del cache

        Args:
            key: Clave a eliminar

        Returns:
            True si se eliminó exitosamente
        """
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error al eliminar del cache: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Eliminar todas las claves que coincidan con un patrón

        Args:
            pattern: Patrón de búsqueda (ej: "movies:*")

        Returns:
            Número de claves eliminadas
        """
        if not self.redis_client:
            return 0

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Error al limpiar patrón: {e}")
            return 0


# Instancia global del servicio de cache
cache_service = CacheService()