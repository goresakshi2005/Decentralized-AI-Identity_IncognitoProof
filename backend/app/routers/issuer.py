from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import json
from cryptography.fernet import Fernet
from app.database import get_db
from app.models import User, Credential, CredentialStatus, AuditEvent
from app.schemas import CredentialCreate, CredentialResponse
from app.routers.auth import get_current_user
from app.services.blockchain_service import anchor_credential
from app.config import settings

router = APIRouter()
# In production, use proper key management
cipher = Fernet(Fernet.generate_key())

@router.post("/credentials", response_model=CredentialResponse)
def issue_credential(
    credential_data: CredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is issuer
    if current_user.role not in ["issuer", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to issue credentials")
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == credential_data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    # Encrypt claim data
    claim_data_json = json.dumps(credential_data.claim_data)
    encrypted_claim = cipher.encrypt(claim_data_json.encode())
    
    # Create credential
    credential_id = f"cred_{uuid.uuid4().hex[:16]}"
    credential = Credential(
        credential_id=credential_id,
        user_id=credential_data.user_id,
        issuer_id=current_user.id,
        claim_type=credential_data.claim_type,
        claim_data_encrypted=encrypted_claim.decode(),
        issued_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=credential_data.expiry_days),
        status=CredentialStatus.ACTIVE
    )
    
    # Sign credential (simplified signature)
    signature_data = f"{credential_id}{credential_data.user_id}{credential_data.claim_type}"
    credential.signature = f"sig_{hash(signature_data)}"
    
    db.add(credential)
    db.commit()
    db.refresh(credential)
    
    # Anchor on blockchain
    try:
        tx_hash = anchor_credential(credential.credential_id, credential.signature)
        credential.blockchain_hash = tx_hash
        db.commit()
    except Exception as e:
        print(f"Blockchain anchoring failed: {e}")
    
    # Log audit
    audit = AuditEvent(
        event_type="credential_issued",
        user_id=current_user.id,
        target_id=credential_id,
        details={"user_id": credential_data.user_id, "claim_type": credential_data.claim_type},
        ip_address="127.0.0.1",  # Get from request
        tamper_hash=f"hash_{datetime.utcnow().timestamp()}"
    )
    db.add(audit)
    db.commit()
    
    return credential

@router.get("/credentials")
def get_issued_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    credentials = db.query(Credential).filter(Credential.issuer_id == current_user.id).all()
    return credentials

@router.post("/revoke/{credential_id}")
def revoke_credential(
    credential_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    credential = db.query(Credential).filter(Credential.credential_id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if credential.issuer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to revoke this credential")
    
    credential.status = CredentialStatus.REVOKED
    credential.revocation_reason = reason
    
    # Add revocation record
    from app.models import RevocationRecord
    revocation = RevocationRecord(
        credential_id=credential.id,
        revoked_by=current_user.id,
        revocation_reason=reason,
        blockchain_hash=f"revoke_{hash(credential_id)}"
    )
    db.add(revocation)
    db.commit()
    
    # Anchor revocation on blockchain
    try:
        from app.services.blockchain_service import revoke_credential_on_chain
        tx_hash = revoke_credential_on_chain(credential_id)
        revocation.blockchain_hash = tx_hash
        db.commit()
    except Exception as e:
        print(f"Blockchain revocation failed: {e}")
    
    return {"message": "Credential revoked successfully"}