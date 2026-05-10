from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json
from app.database import get_db
from app.models import Credential, ZKProofRecord, ProofRequest, ProofResponse
from app.schemas import ZKProofGenerateRequest, ZKProofResponse
from app.routers.auth import get_current_user
from app.services.zk_service import get_zk_provider, ZKProvider
from app.services.consent_service import check_consent

router = APIRouter()
zk_provider: ZKProvider = get_zk_provider()

@router.post("/generate-proof", response_model=ZKProofResponse)
async def generate_proof(
    request: ZKProofGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get credential
    credential = db.query(Credential).filter(
        Credential.id == request.credential_id,
        Credential.user_id == current_user.id
    ).first()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if credential.status != "active":
        raise HTTPException(status_code=400, detail="Credential is not active")
    
    # Check expiry
    if credential.expiry_date < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Credential expired")
    
    # Decrypt claim data (simplified)
    from cryptography.fernet import Fernet
    cipher = Fernet(Fernet.generate_key())  # In production, use stored key
    claim_data = json.loads(cipher.decrypt(credential.claim_data_encrypted.encode()))
    
    # Prepare witness for ZK proof
    witness = {
        "claim_type": request.claim_type,
        "predicate": request.predicate,
        "data": claim_data
    }
    
    # Generate ZK proof
    proof_id = f"proof_{uuid.uuid4().hex[:16]}"
    proof_result = await zk_provider.generate_proof(proof_id, witness)
    
    # Store proof record
    zk_record = ZKProofRecord(
        proof_id=proof_id,
        credential_id=credential.id,
        claim_type=request.claim_type,
        public_inputs=proof_result["public_signals"],
        proof_data=proof_result["proof"],
        verification_key=zk_provider.get_verification_key()
    )
    db.add(zk_record)
    db.commit()
    
    return ZKProofResponse(
        proof_id=proof_id,
        proof_data=proof_result["proof"],
        public_signals=proof_result["public_signals"],
        verified=False
    )

@router.post("/verify-proof")
async def verify_proof(
    proof_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Retrieve proof
    proof_record = db.query(ZKProofRecord).filter(ZKProofRecord.proof_id == proof_id).first()
    if not proof_record:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    # Check consent
    if not check_consent(current_user.id, proof_record.credential.user_id, proof_id):
        raise HTTPException(status_code=403, detail="Consent not granted")
    
    # Verify proof
    verification_result = await zk_provider.verify_proof(
        proof_record.proof_data,
        proof_record.public_inputs
    )
    
    proof_record.verified = verification_result["verified"]
    db.commit()
    
    return {
        "verified": verification_result["verified"],
        "message": verification_result.get("message", ""),
        "claims": verification_result.get("claims", {})
    }