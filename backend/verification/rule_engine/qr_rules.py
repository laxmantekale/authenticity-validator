import re
from urllib.parse import urlparse
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from utils.document_utils import get_cv2_images_from_file

class QRRules:
    """
    Decodes, secures, and verifies QR codes embedded on documents.
    """

    BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"}

    @classmethod
    def decode_qr(cls, file_path: str) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
        """
        Attempts to detect and decode QR codes from all document pages using OpenCV QRCodeDetector.
        """
        images = get_cv2_images_from_file(file_path, max_pages=5)
        if not images:
            return False, None, None

        detector = cv2.QRCodeDetector()
        for img in images:
            try:
                data, bbox, _ = detector.detectAndDecode(img)
                if data and len(data.strip()) > 0:
                    return True, data.strip(), bbox
            except Exception:
                continue

        return False, None, None

    @classmethod
    def validate_qr_security(cls, qr_payload: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Performs SSRF and URL safety validation on QR contents.
        """
        if not qr_payload:
            return False, "Empty QR payload", {}

        # If payload is a URL
        if qr_payload.startswith("http://") or qr_payload.startswith("https://"):
            try:
                parsed = urlparse(qr_payload)
                host = parsed.hostname or ""

                if host.lower() in cls.BLOCKED_HOSTS or host.startswith("192.168.") or host.startswith("10."):
                    return False, "Security Alert: QR contains private / loopback IP address (SSRF blocked)", {"unsafe": True}

                if parsed.scheme not in ["http", "https"]:
                    return False, f"Security Alert: Unsupported URI scheme '{parsed.scheme}'", {"unsafe": True}

                return True, "Valid secure web URL format", {
                    "type": "URL",
                    "domain": host,
                    "url": qr_payload
                }
            except Exception as e:
                return False, f"Malformed URL in QR code: {e}", {"unsafe": True}

        # Structured Text / Token Payload
        return True, "Valid structured document verification token / payload", {
            "type": "TOKEN_OR_DATA",
            "length": len(qr_payload)
        }

    @classmethod
    def verify_qr(cls, file_path: str, ocr_text: str = "") -> Dict[str, Any]:
        """
        Complete QR verification pipeline:
        - Detect & Decode
        - Security Check
        - Content Consistency Comparison against OCR text
        """
        found, payload, _ = cls.decode_qr(file_path)

        if not found or not payload:
            return {
                "status": "NOT_APPLICABLE",
                "present": False,
                "message": "No QR Code detected on document",
                "details": None
            }

        is_safe, sec_msg, sec_info = cls.validate_qr_security(payload)
        if not is_safe:
            return {
                "status": "FAILED",
                "present": True,
                "message": sec_msg,
                "details": sec_info
            }

        # Check if QR payload shares matching tokens with OCR text
        ocr_lower = (ocr_text or "").lower()
        payload_lower = payload.lower()
        matched_tokens = []

        # Find any 4+ char alphanumeric tokens in QR that appear in OCR
        tokens = re.findall(r'[A-Za-z0-9]{4,}', payload_lower)
        for tok in tokens:
            if tok in ocr_lower and not tok.startswith("http"):
                matched_tokens.append(tok)

        return {
            "status": "PASSED",
            "present": True,
            "message": "QR Code successfully decoded and verified",
            "payload_type": sec_info.get("type", "DATA"),
            "qr_data_sample": payload[:60] + "..." if len(payload) > 60 else payload,
            "matched_tokens_count": len(matched_tokens)
        }
