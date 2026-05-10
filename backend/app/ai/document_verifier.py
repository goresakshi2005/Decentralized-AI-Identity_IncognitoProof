import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import base64
import re
from typing import Dict, Tuple

class DocumentVerifier:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    async def verify_document(self, document_image_b64: str) -> Dict:
        """Verify document authenticity and extract data"""
        # Decode base64 image
        image_data = base64.b64decode(document_image_b64.split(',')[1] if ',' in document_image_b64 else document_image_b64)
        image = Image.open(io.BytesIO(image_data))
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # OCR extraction
        extracted_text = pytesseract.image_to_string(image, lang='eng')
        
        # Document authenticity checks
        authenticity_score, issues = self._check_authenticity(cv_image)
        
        # Extract structured data
        extracted_data = self._extract_structured_data(extracted_text)
        
        return {
            "authenticity_score": authenticity_score,
            "extracted_text": extracted_text,
            "extracted_data": extracted_data,
            "issues": issues,
            "is_tampered": authenticity_score < 0.7
        }
    
    def _check_authenticity(self, image: np.ndarray) -> Tuple[float, list]:
        """Check for tampering, blur, inconsistent fonts"""
        issues = []
        score = 1.0
        
        # Check image blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 100:
            score -= 0.2
            issues.append("Blurry image detected")
        
        # Check for compression artifacts
        # Simplified - in production use more sophisticated methods
        
        # Check edge consistency
        edges = cv2.Canny(gray, 50, 150)
        if np.sum(edges) / edges.size < 0.05:
            score -= 0.1
            issues.append("Inconsistent edges")
        
        return max(0, min(1, score)), issues
    
    def _extract_structured_data(self, text: str) -> Dict:
        """Extract name, DOB, document number etc."""
        data = {}
        
        # Name extraction (simplified regex)
        name_match = re.search(r'Name[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Date of birth extraction
        dob_match = re.search(r'DOB[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', text, re.IGNORECASE)
        if dob_match:
            data['dob'] = dob_match.group(1)
        
        # Document number
        doc_match = re.search(r'(ID|Passport|Number)[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
        if doc_match:
            data['document_number'] = doc_match.group(2)
        
        return data