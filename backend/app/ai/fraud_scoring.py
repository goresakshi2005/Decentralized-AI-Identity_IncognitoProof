import numpy as np
from typing import Dict, List
from datetime import datetime
from sklearn.ensemble import IsolationForest

class FraudScoringEngine:
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavioral_features = []
    
    async def compute_fraud_score(self, verification_data: Dict) -> Dict:
        """Combine all signals into final fraud score"""
        authenticity_score = verification_data.get('authenticity_score', 0)
        face_match_score = verification_data.get('face_match_score', 0)
        liveness_score = verification_data.get('liveness_score', 0)
        deepfake_score = verification_data.get('deepfake_score', 0)
        behavioral_risk = verification_data.get('behavioral_risk', 0)
        
        # Weighted scoring
        weights = {
            'authenticity': 0.3,
            'face_match': 0.25,
            'liveness': 0.2,
            'deepfake': 0.15,
            'behavioral': 0.1
        }
        
        total_risk = (
            (1 - authenticity_score) * weights['authenticity'] +
            (1 - face_match_score) * weights['face_match'] +
            (1 - liveness_score) * weights['liveness'] +
            deepfake_score * weights['deepfake'] +
            behavioral_risk * weights['behavioral']
        )
        
        # Determine decision
        if total_risk < 0.3:
            decision = "APPROVED"
        elif total_risk < 0.7:
            decision = "REVIEW"
        else:
            decision = "REJECTED"
        
        # Generate flags
        flags = []
        if authenticity_score < 0.7:
            flags.append("suspicious_document")
        if face_match_score < 0.6:
            flags.append("face_mismatch")
        if liveness_score < 0.7:
            flags.append("liveness_failed")
        if deepfake_score > 0.6:
            flags.append("deepfake_suspected")
        
        return {
            "total_risk": float(total_risk),
            "decision": decision,
            "flags": flags,
            "breakdown": {
                "authenticity": float(authenticity_score),
                "face_match": float(face_match_score),
                "liveness": float(liveness_score),
                "deepfake": float(deepfake_score),
                "behavioral": float(behavioral_risk)
            }
        }
    
    async def detect_anomalies(self, user_history: List[Dict]) -> float:
        """Detect anomalous behavior patterns"""
        if len(user_history) < 5:
            return 0.0
        
        # Extract features
        features = []
        for record in user_history[-20:]:  # Last 20 records
            feature_vector = [
                record.get('authenticity_score', 0),
                record.get('face_match_score', 0),
                record.get('liveness_score', 0),
                1 if record.get('decision') == 'REJECTED' else 0,
                record.get('attempt_count', 1)
            ]
            features.append(feature_vector)
        
        # Fit and predict anomaly
        if len(features) >= 10:
            self.anomaly_detector.fit(features)
            predictions = self.anomaly_detector.predict(features)
            anomaly_count = sum(1 for p in predictions if p == -1)
            return min(1.0, anomaly_count / len(features))
        
        return 0.0