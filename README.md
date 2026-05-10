# py-rate-limiter

API em FastAPI com rate limiting implementado do zero, usando Redis. Suporta dois algoritmos: **Token Bucket** e **Sliding Window**.

## Pré-requisitos

- Python 3.10+
- Redis rodando localmente na porta `6379`

## Instalação

```bash
# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
pip install httpx  # para o script de teste
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_ALGORITHM=token_bucket  # ou sliding_window
```

## Rodando a API

```bash
uvicorn main:app --reload --port 8000
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

## Testando o rate limiter

### Script Python (recomendado)

Faz 15 requisições seguidas — as 10 primeiras retornam `200`, as demais retornam `429`:

```bash
python test_rate_limiter.py
```

Saída esperada:

```
Req 1: 200
Req 2: 200
...
Req 10: 200
Req 11: 429
  → {'error': 'Too Many Requests', 'message': 'Limite excedido. Tente novamente em Xs', 'retry_after': X}
```

### curl (bash/WSL)

```bash
for i in {1..11}; do
  echo "Requisição $i:"
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/test
done
```

## Rotas

| Método | Rota           | Rate limit | Descrição                  |
|--------|----------------|------------|----------------------------|
| GET    | `/test`        | Sim        | Rota de teste              |
| GET    | `/api/resource`| Sim        | Recurso protegido          |
| GET    | `/health`      | Não        | Health check               |
| GET    | `/docs`        | Não        | Documentação Swagger       |

## Algoritmos disponíveis

**Token Bucket** (`RATE_LIMIT_ALGORITHM=token_bucket`)  
Mantém um balde de tokens que se reabastece ao longo do tempo. Permite pequenas rajadas enquanto mantém a taxa média controlada.

**Sliding Window** (`RATE_LIMIT_ALGORITHM=sliding_window`)  
Conta as requisições dentro de uma janela de tempo deslizante. Controle mais preciso que a janela fixa.

## Estrutura do projeto

```
py-rate-limiter/
├── main.py                      # Entrypoint FastAPI
├── config.py                    # Configurações via .env
├── test_rate_limiter.py         # Script de teste
├── domain/
│   ├── interfaces.py            # Interface RateLimiterStrategy
│   └── exceptions.py           # Exceções de domínio
├── infra/
│   ├── redis_client.py          # Cliente Redis
│   └── algorithms/
│       ├── token_bucket.py      # Algoritmo Token Bucket
│       └── sliding_window.py    # Algoritmo Sliding Window
└── middleware/
    └── rate_limit_middleware.py # Middleware FastAPI
```
