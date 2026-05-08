import time
import redis.asyncio as aioredis
from domain.interfaces import RateLimiterStrategy
from config import settings

class TokenBucketStrategy(RateLimiterStrategy):
    """

    Algoritmo Token Bucket implementado com Redis.
    """

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.max_tokens = settings.RATE_LIMIT_MAX_REQUESTS
        self.refill_rate = settings.RATE_LIMIT_MAX_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS

    def _get_bucket_key(self, client_id: str) -> str:
        """

        Gera a chave no Redis para o balde deste cliente.
        """
        return f"tb:{client_id}"
    
    async def is_allowed(self, client_id: str) -> bool:
        """

        Verifica se o cliente pode fazer a requisição.
        """
        key = self._get_bucket_key(client_id)
        now = time.time()

        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local max_tokens = tonumber(ARGV[2])
        local refill_rate = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])
        
        -- Busca os dados atuais do balde
        local data = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(data[1]) or max_tokens  -- se não existe, começa cheio
        local last_refill = tonumber(data[2]) or now
        
        -- Calcula quanto tempo passou desde o último reabastecimento
        local elapsed = now - last_refill
        
        -- Calcula quantos tokens adicionar proporcionalmente ao tempo
        -- Ex: se passaram 30s numa janela de 60s, adiciona metade dos tokens
        local tokens_to_add = (elapsed / window) * refill_rate
        
        -- Adiciona os tokens, respeitando o máximo
        tokens = math.min(max_tokens, tokens + tokens_to_add)
        
        -- Verifica se tem token disponível
        if tokens >= 1 then
            tokens = tokens - 1  -- consome 1 token
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, window * 2)  -- expira após 2 janelas sem uso
            return 1  -- permitido
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            return 0  -- bloqueado
        end
        """

        result = await self.redis.eval(
            lua_script,
           1,                     # número de KEYS
            key,                  # KEYS[1]
            now,                  # ARGV[1]
            self.max_tokens,      # ARGV[2]
            self.refill_rate,     # ARGV[3]
            self.window,          # ARGV[4]
        )

        return result == 1
    
    async def get_retry_after(self, client_id: str) -> int:
        """

        Retorna o tempo em segundos até o próximo token estar disponível.
        """

        key = self._get_bucket_key(client_id)
        data = await self.redis.hmget(key, 'tokens', 'last_refill')

        tokens = float(data[0] or 0)
        last_refill = float(data[1] or time.time())

        tokens_needed = 1 - tokens
        seconds_needed = (tokens_needed / self.refill_rate) * self.window
        
        return max(1, int(seconds_needed))