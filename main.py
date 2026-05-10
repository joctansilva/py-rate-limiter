from contextlib import asynccontextmanager
from fastapi import FastAPI
from infra.redis_client import RedisClient
from infra.algorithms import create_rate_limiter_strategy
from middleware.rate_limit_middleware import RateLimitMiddleware

# Lifespan gerencia o que acontece ao iniciar e encerrar a aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicação...")

    # Cria e injeta a estratégia de rate limiting na aplicação
    redis_client = RedisClient.get_client()
    strategy = create_rate_limiter_strategy(redis_client)
    app.state.rate_limiter = strategy

    print(f"Rate limiter ativo: {strategy.__class__.__name__}")

    yield  # A aplicação roda aqui

    print("Encerrando aplicação...")
    await RedisClient.close()

app = FastAPI(
    title="Rate Limiter do Zero",
    description="Rate limiter implementado com Token Bucket e Sliding Window",
    lifespan=lifespan,
)

# Adiciona o middleware, ele intercepta TODAS as requisições
# O middleware é adicionado DEPOIS de criar o app e ANTES das rotas
app.add_middleware(RateLimitMiddleware)

# Rota de health check, não tem rate limit (configurado no middleware)
@app.get("/health")
async def health():
    """Verifica se a API está no ar."""
    return {"status": "ok"}

# Rota de teste para verificar o rate limiting
@app.get("/test")
async def test_endpoint():
    """Rota de teste. Faça mais de 10 requisições em 60s para ver o 429."""
    return {"message": "Requisição aceita!", "status": "ok"}

# Rota que simula um recurso protegido
@app.get("/api/resource")
async def get_resource():
    """Recurso protegido pelo rate limiter."""
    return {"data": "Dados do recurso", "protected": True}