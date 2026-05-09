import redis.asyncio as aioredis
from domain.interfaces import RateLimiterStrategy
from config import settings
from .token_bucket import TokenBucketStrategy
from .sliding_window import SlidingWindowStrategy

def create_rate_limiter_strategy(redis_client: aioredis.Redis) -> RateLimiterStrategy:
    """
    
    Factory function: decide qual algoritmo usar com base na configuração.
    """
    algorithm = settings.RATE_LIMIT_ALGORITHM

    if algorithm == "sliding_window":
        return SlidingWindowStrategy(redis_client)

    # Token Bucket é o padrão
    return TokenBucketStrategy(redis_client)