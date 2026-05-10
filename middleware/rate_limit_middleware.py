from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from domain.interfaces import RateLimiterStrategy
from domain.exceptions import RateLimitExceededException

class RateLimitMiddleware(BaseHTTPMiddleware):
    """

    Middleware do FastAPI que intercepta todas as requisições.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """

        Intercepta a requisição antes de chegar na rota.
        """

        client_id = request.client.host if request.client else "unknown"

        # Não aplica rate limit em rotas de health check
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        strategy: RateLimiterStrategy = request.app.state.rate_limiter

        try:
            is_allowed = await strategy.is_allowed(client_id)

            if not is_allowed:
                retry_after = await strategy.get_retry_after(client_id)

                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": f"Limite excedido. Tente novamente em {retry_after}s",
                        "retry_after": retry_after,
                    },
                    headers={
                        # informar quando tentar de novo
                        "Retry-After": str(retry_after),
                        # limite configurado
                        "X-RateLimit-Limit": str(strategy.__class__.__name__),
                    },
                )

            response = await call_next(request)
            return response

        except Exception as e:

            print(f"[RateLimiter] Erro ao verificar rate limit: {e}")
            return await call_next(request)