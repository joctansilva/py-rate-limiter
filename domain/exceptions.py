class RateLimitExceededException(Exception):
    """
    Exceção de domínio lançada quando o cliente excede o limite.
    """
    def __init__(self, retry_after: int):
        #retry_after define quantos segundos o cliente deve esperar antes de tentar novamente
        self.retry_after = retry_after
        super().__init__(f"Rate limit excedido. Tente novamente em {retry_after}s")