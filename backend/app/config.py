from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/identity_db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Blockchain
    BLOCKCHAIN_RPC_URL: str = "http://localhost:8545"
    CREDENTIAL_REGISTRY_ADDRESS: Optional[str] = None
    REVOCATION_REGISTRY_ADDRESS: Optional[str] = None
    ISSUER_REGISTRY_ADDRESS: Optional[str] = None
    
    # AI settings
    OCR_LANGUAGE: str = "eng"
    FACE_MATCH_THRESHOLD: float = 0.6
    LIVENESS_THRESHOLD: float = 0.7
    DEEPFAKE_THRESHOLD: float = 0.5
    
    # ZK Settings
    ZK_PROVIDER: str = "mock"  # "mock" or "circom"
    ZK_CIRCUIT_PATH: str = "./app/zk/circuits"
    
    class Config:
        env_file = ".env"

settings = Settings()