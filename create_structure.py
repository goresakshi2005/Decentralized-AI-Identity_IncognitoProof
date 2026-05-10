import os

structure = {
    "backend/app/routers": ["auth.py", "wallet.py", "issuer.py", "verifier.py", "consent.py", "ai.py", "admin.py", "blockchain.py", "zk.py"],
    "backend/app/services": ["did_service.py", "credential_service.py", "zk_service.py", "blockchain_service.py", "consent_service.py", "audit_service.py", "revocation_service.py"],
    "backend/app/ai": ["document_verifier.py", "face_verifier.py", "liveness.py", "deepfake.py", "fraud_scoring.py", "anomaly_detection.py"],
    "backend/app/zk/circuits": ["age_circuit.circom", "proof.json", "verification_key.json"],
    "backend/app/zk": ["__init__.py", "base.py", "mock_provider.py", "circom_provider.py"],
    "backend/app/utils": ["security.py", "encryption.py", "logging.py"],
    "backend/app": ["__init__.py", "main.py", "config.py", "database.py", "models.py", "schemas.py", "dependencies.py"],
    "backend": ["requirements.txt", "Dockerfile", ".env.example"],
    
    "frontend/src/components/Layout": [],
    "frontend/src/components/Auth": [],
    "frontend/src/components/Dashboard": [],
    "frontend/src/components/Wallet": [],
    "frontend/src/components/Credentials": [],
    "frontend/src/components/Proofs": [],
    "frontend/src/components/Consent": [],
    "frontend/src/components/Admin": [],
    "frontend/src/components/Common": [],
    
    "frontend/src/pages": ["Landing.jsx", "Login.jsx", "Register.jsx", "UserDashboard.jsx", "IssuerDashboard.jsx", "VerifierDashboard.jsx", "AdminDashboard.jsx", "Wallet.jsx"],
    "frontend/src/contexts": ["AuthContext.jsx", "Web3Context.jsx"],
    "frontend/src/services": ["api.js", "blockchain.js"],
    "frontend/src": ["App.jsx", "main.jsx", "index.css"],
    "frontend": ["package.json", "vite.config.js", "Dockerfile", ".env.example"],
    
    "blockchain/contracts": ["CredentialRegistry.sol", "RevocationRegistry.sol", "IssuerRegistry.sol"],
    "blockchain/scripts": ["deploy.js", "seed.js"],
    "blockchain/test": [],
    "blockchain": ["hardhat.config.js", ".env.example"],
    
    ".": ["docker-compose.yml", "README.md", ".gitignore"]
}

base_path = r"e:\Projects\Decentrallized-AI-Identity"

for folder, files in structure.items():
    folder_path = os.path.join(base_path, folder)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "w") as f:
            pass

print("Directory structure created successfully.")
