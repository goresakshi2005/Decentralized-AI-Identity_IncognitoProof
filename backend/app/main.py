from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.database import engine, Base
from app.routers import auth, wallet, issuer, verifier, consent, ai, admin, blockchain, zk
from app.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Decentralized AI Identity Verification", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(issuer.router, prefix="/api/issuer", tags=["Issuer"])
app.include_router(verifier.router, prefix="/api/verifier", tags=["Verifier"])
app.include_router(consent.router, prefix="/api/consent", tags=["Consent"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Verification"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(blockchain.router, prefix="/api/blockchain", tags=["Blockchain"])
app.include_router(zk.router, prefix="/api/zk", tags=["Zero-Knowledge"])

@app.get("/")
def root():
    return {"message": "Decentralized AI Identity Verification API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}