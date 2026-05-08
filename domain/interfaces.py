from abc import ABC, abstractmethod

class RateLimiterStrategy(ABC):
    """
    Interface abstrata que define o contrato do rate limiter.
    """
    @abstractmethod
    def is_allowed(self, client_id: str) -> bool:
        """
        Verifica se a requisição do cliente é permitida.
        """
        pass

    @abstractmethod
    async def get_retry_after(self, client_id: str) -> int:
        """
        Retorna quantos segundos o cliente deve esperar.
        """
        pass