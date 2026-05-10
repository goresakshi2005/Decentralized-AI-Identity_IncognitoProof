import face_recognition
import numpy as np
import base64
from PIL import Image
import io
from typing import Tuple

class FaceVerifier:
    def __init__(self, threshold=0.6):
        self.threshold = threshold
    
    async def verify_face_match(self, document_face_b64: str, selfie_b64: str) -> dict:
        """Compare face from document with selfie"""
        # Load images
        doc_face = self._load_face_encoding(document_face_b64)
        selfie = self._load_face_encoding(selfie_b64)
        
        if doc_face is None or selfie is None:
            return {
                "match": False,
                "similarity": 0.0,
                "error": "Face not detected in one or both images"
            }
        
        # Compute face distance
        face_distance = face_recognition.face_distance([doc_face], selfie)[0]
        similarity = 1 - face_distance  # Convert distance to similarity
        
        # Check match
        is_match = similarity >= self.threshold
        
        return {
            "match": is_match,
            "similarity": float(similarity),
            "threshold": self.threshold
        }
    
    def _load_face_encoding(self, image_b64: str):
        """Extract face encoding from base64 image"""
        try:
            # Decode base64
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB numpy array
            image_np = np.array(image)
            
            # Get face encodings
            face_locations = face_recognition.face_locations(image_np)
            if not face_locations:
                return None
            
            encodings = face_recognition.face_encodings(image_np, face_locations)
            if not encodings:
                return None
            
            return encodings[0]
        except Exception as e:
            print(f"Face encoding error: {e}")
            return None