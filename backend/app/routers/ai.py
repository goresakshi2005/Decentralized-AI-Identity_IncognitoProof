from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, FraudScore, DocumentUpload, FaceMatchResult, AuditEvent
from app.schemas import AIVerificationRequest, AIVerificationResponse
from app.routers.auth import get_current_user
from app.ai.document_verifier import DocumentVerifier
from app.ai.face_verifier import FaceVerifier
from app.ai.liveness import LivenessDetector
from app.ai.deepfake import DeepfakeDetector
from app.ai.fraud_scoring import FraudScoringEngine
import uuid

router = APIRouter()
doc_verifier = DocumentVerifier()
face_verifier = FaceVerifier()
liveness_detector = LivenessDetector()
deepfake_detector = DeepfakeDetector()
fraud_engine = FraudScoringEngine()

@router.post("/verify-document", response_model=AIVerificationResponse)
async def verify_document(
    request: AIVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_id = str(uuid.uuid4())
    
    # Run document verification
    doc_result = await doc_verifier.verify_document(request.document_image)
    
    # Run face verification
    face_result = await face_verifier.verify_face_match(
        doc_result.get('extracted_data', {}).get('face_image', request.document_image),
        request.selfie_image
    )
    
    # Run liveness detection
    liveness_result = await liveness_detector.check_liveness(request.selfie_image)
    
    # Run deepfake detection
    deepfake_result = await deepfake_detector.detect(request.selfie_image)
    
    # Get behavioral risk (simplified)
    behavioral_risk = 0.1  # Placeholder
    
    # Compute final fraud score
    fraud_result = await fraud_engine.compute_fraud_score({
        'authenticity_score': doc_result['authenticity_score'],
        'face_match_score': face_result['similarity'],
        'liveness_score': liveness_result['score'],
        'deepfake_score': deepfake_result['score'],
        'behavioral_risk': behavioral_risk
    })
    
    # Store results in database
    fraud_score = FraudScore(
        user_id=current_user.id,
        verification_session_id=session_id,
        authenticity_score=doc_result['authenticity_score'],
        face_match_score=face_result['similarity'],
        liveness_score=liveness_result['score'],
        deepfake_score=deepfake_result['score'],
        total_fraud_risk=fraud_result['total_risk'],
        final_decision=fraud_result['decision'],
        flags=fraud_result['flags']
    )
    db.add(fraud_score)
    
    # Store document
    doc_upload = DocumentUpload(
        user_id=current_user.id,
        session_id=session_id,
        document_type="id_card",
        file_path_encrypted="encrypted_path",  # In production, store encrypted
        ocr_extracted_text=doc_result['extracted_text'],
        checksum=f"hash_{session_id}"
    )
    db.add(doc_upload)
    
    # Store face match
    face_match = FaceMatchResult(
        session_id=session_id,
        selfie_path="encrypted_selfie_path",
        document_face_path="encrypted_doc_face_path",
        similarity_score=face_result['similarity'],
        verified=face_result['match']
    )
    db.add(face_match)
    
    db.commit()
    
    # Log audit
    audit = AuditEvent(
        event_type="ai_verification",
        user_id=current_user.id,
        target_id=session_id,
        details={"decision": fraud_result['decision'], "risk_score": fraud_result['total_risk']},
        ip_address="127.0.0.1",
        tamper_hash=f"hash_{session_id}"
    )
    db.add(audit)
    db.commit()
    
    return AIVerificationResponse(
        session_id=session_id,
        authenticity_score=doc_result['authenticity_score'],
        face_match_score=face_result['similarity'],
        liveness_score=liveness_result['score'],
        deepfake_score=deepfake_result['score'],
        fraud_risk_score=fraud_result['total_risk'],
        decision=fraud_result['decision'],
        flags=fraud_result['flags']
    )