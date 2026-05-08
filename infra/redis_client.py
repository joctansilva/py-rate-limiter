import redis.asyncio as aioredis
from config import settings

class RedisClient:
    """
    Wrapper do cliente Redis.
    """

    _client: aioredis.Redis = None

    @classmethod
    def get_client(cls) -> aioredis.Redis:
        """        
        Retorna o cliente Redis, criando a conexão se necessário.
        """

        if cls._client is None:
            cls._client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        return cls._client
    

    @classmethod
    async def close(cls):
        """
        Fecha a conexão com o Redis quando a aplicação encerra.
        """
        if cls._client:
            await cls._client.close()
            cls._client = None