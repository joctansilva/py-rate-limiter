import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Limite: 10 requisições por 60 segundos
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # Qual algoritmo usar: "token_bucket" ou "sliding_window"
    RATE_LIMIT_ALGORITHM: str = os.getenv("RATE_LIMIT_ALGORITHM", "token_bucket")

settings = Settings()