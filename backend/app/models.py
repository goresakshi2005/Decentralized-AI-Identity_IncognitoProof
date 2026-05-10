from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ISSUER = "issuer"
    VERIFIER = "verifier"
    ADMIN = "admin"

class CredentialStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    did_profile = relationship("DIDProfile", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    credentials = relationship("Credential", back_populates="user")
    consent_records = relationship("ConsentRecord", back_populates="user")
    verification_logs = relationship("VerificationLog", back_populates="user")
    fraud_scores = relationship("FraudScore", back_populates="user")

class DIDProfile(Base):
    __tablename__ = "did_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    did = Column(String, unique=True, index=True)
    public_key = Column(Text)
    private_key_encrypted = Column(Text)
    method = Column(String, default="key")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="did_profile")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    blockchain_address = Column(String, unique=True, nullable=True)
    encrypted_private_key = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="wallet")

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    issuer_id = Column(Integer, ForeignKey("users.id"))
    claim_type = Column(String, index=True)  # age_proof, student_id, employee_id, kyc_verified
    claim_data_encrypted = Column(Text)  # Encrypted claim data
    signature = Column(Text)  # Issuer's signature
    issued_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    status = Column(Enum(CredentialStatus), default=CredentialStatus.ACTIVE)
    revocation_reason = Column(String, nullable=True)
    blockchain_hash = Column(String, nullable=True)  # Transaction hash
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", foreign_keys=[user_id], back_populates="credentials")
    issuer = relationship("User", foreign_keys=[issuer_id])
    proof_requests = relationship("ProofRequest", back_populates="credential")

class ProofRequest(Base):
    __tablename__ = "proof_requests"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    verifier_id = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    credential_id = Column(Integer, ForeignKey("credentials.id"))
    claim_type = Column(String)
    predicate = Column(JSON)  # e.g., {"age": {"gte": 18}}
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    status = Column(String, default="pending")  # pending, approved, rejected, completed
    
    credential = relationship("Credential", back_populates="proof_requests")
    verifier = relationship("User", foreign_keys=[verifier_id])
    user = relationship("User", foreign_keys=[user_id])
    proof_response = relationship("ProofResponse", back_populates="proof_request", uselist=False)

class ProofResponse(Base):
    __tablename__ = "proof_responses"
    id = Column(Integer, primary_key=True, index=True)
    proof_request_id = Column(Integer, ForeignKey("proof_requests.id"), unique=True)
    zk_proof = Column(Text)  # Serialized proof
    public_signals = Column(JSON)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
    verification_result = Column(Boolean)
    
    proof_request = relationship("ProofRequest", back_populates="proof_response")

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    verifier_id = Column(Integer, ForeignKey("users.id"))
    proof_request_id = Column(Integer, ForeignKey("proof_requests.id"))
    consent_given = Column(Boolean)
    consent_details = Column(JSON)  # What data is shared/not shared
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="consent_records")
    proof_request = relationship("ProofRequest")

class VerificationLog(Base):
    __tablename__ = "verification_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    verifier_id = Column(Integer, ForeignKey("users.id"))
    claim_type = Column(String)
    result = Column(Boolean)
    proof_valid = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    blockchain_tx = Column(String, nullable=True)
    
    user = relationship("User", back_populates="verification_logs")
    verifier = relationship("User", foreign_keys=[verifier_id])

class RevocationRecord(Base):
    __tablename__ = "revocation_records"
    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"), unique=True)
    revoked_by = Column(Integer, ForeignKey("users.id"))
    revocation_reason = Column(String)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    blockchain_hash = Column(String)
    
    credential = relationship("Credential")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_id = Column(String, nullable=True)
    details = Column(JSON)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tamper_hash = Column(String, unique=True)  # SHA256 chain hash

class FraudScore(Base):
    __tablename__ = "fraud_scores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    verification_session_id = Column(String, index=True)
    authenticity_score = Column(Float)
    face_match_score = Column(Float)
    liveness_score = Column(Float)
    deepfake_score = Column(Float)
    total_fraud_risk = Column(Float)
    final_decision = Column(String)  # APPROVED, REVIEW, REJECTED
    flags = Column(JSON)  # List of flags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="fraud_scores")

class DocumentUpload(Base):
    __tablename__ = "document_uploads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, index=True)
    document_type = Column(String)
    file_path_encrypted = Column(String)
    ocr_extracted_text = Column(Text, nullable=True)
    checksum = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FaceMatchResult(Base):
    __tablename__ = "face_match_results"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    selfie_path = Column(String)
    document_face_path = Column(String)
    similarity_score = Column(Float)
    verified = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ZKProofRecord(Base):
    __tablename__ = "zk_proof_records"
    id = Column(Integer, primary_key=True, index=True)
    proof_id = Column(String, unique=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"))
    claim_type = Column(String)
    public_inputs = Column(JSON)
    proof_data = Column(Text)
    verification_key = Column(String)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    credential = relationship("Credential")