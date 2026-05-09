import time
import redis.asyncio as aioredis
from domain.interfaces import RateLimiterStrategy
from config import settings

class SlidingWindowStrategy(RateLimiterStrategy):
    """

    Algoritmo Sliding Window implementado com Redis Sorted Set.
    """

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.max_requests = settings.RATE_LIMIT_MAX_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS
    
    def _get_window_key(self, client_id: str) -> str:
        """

        Gera a chave no Redis para a janela deste cliente.
        Prefixo 'sw:' identifica que é Sliding Window.
        """
        return f"sw:{client_id}"
    
    async def is_allowed(self, client_id: str) -> bool:
        """

        Usa pipeline do Redis para executar múltiplos comandos eficientemente.
        """
        key = self._get_window_key(client_id)
        now = time.time()
        window_start = now - self.window

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)  # Remove timestamps fora da janela

            pipe.zcard(key)  # Conta quantos timestamps ainda estão na janela

            pipe.zadd(key, {f"{now}:{id(now)}": now})  # Adiciona o timestamp atual

            pipe.expire(key, self.window)  # Define expiração para limpar chaves antigas

            results = await pipe.execute()
        
        current_count = results[1]  # Resultado do zcard   

        if current_count >= self.max_requests:
            await self.redis.zremrangebyscore(key, now, now + 1)  # Remove o timestamp adicionado se exceder o limite
            return False
        
        return True
    
    async def get_retry_after(self, client_id: str) -> int:
        """

        Calcula quando a requisição mais antiga da janela vai expirar.
        """
        key = self._get_window_key(client_id)


        # Obtém o timestamp mais antigo na janela
        oldest = await self.redis.zrange(key, 0, 0, withscores=True)

        if not oldest:
            return 1
        
        oldest_timestamp = oldest[0][1]  # O score é o timestamp

        expires_at = oldest_timestamp + self.window

        retry_after = expires_at - time.time()

        return max(1, int(retry_after))