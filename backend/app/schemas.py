from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ISSUER = "issuer"
    VERIFIER = "verifier"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DIDProfileResponse(BaseModel):
    did: str
    method: str
    created_at: datetime

class CredentialCreate(BaseModel):
    user_id: int
    claim_type: str
    claim_data: Dict[str, Any]
    expiry_days: int = 365

class CredentialResponse(BaseModel):
    credential_id: str
    claim_type: str
    issuer_id: int
    issued_date: datetime
    expiry_date: datetime
    status: str
    blockchain_hash: Optional[str]

class ProofRequestCreate(BaseModel):
    user_id: int
    claim_type: str
    predicate: Dict[str, Any]

class ProofRequestResponse(BaseModel):
    request_id: str
    claim_type: str
    predicate: Dict[str, Any]
    status: str
    requested_at: datetime

class ConsentRequest(BaseModel):
    proof_request_id: int
    verifier_info: Dict[str, str]

class ConsentResponse(BaseModel):
    consent_id: int
    granted: bool
    sharing_details: Dict[str, Any]

class AIVerificationRequest(BaseModel):
    document_image: str  # base64
    selfie_image: str    # base64
    liveness_video: Optional[str] = None

class AIVerificationResponse(BaseModel):
    session_id: str
    authenticity_score: float
    face_match_score: float
    liveness_score: float
    deepfake_score: float
    fraud_risk_score: float
    decision: str  # APPROVED, REVIEW, REJECTED
    flags: List[str]

class ZKProofGenerateRequest(BaseModel):
    credential_id: int
    claim_type: str
    predicate: Dict[str, Any]

class ZKProofResponse(BaseModel):
    proof_id: str
    proof_data: str
    public_signals: List[str]
    verified: bool

class AdminUserUpdate(BaseModel):
    is_active: bool
    role: Optional[UserRole]