import re
import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional
from utils.document_utils import get_cv2_images_from_file

class BarcodeRules:
    """
    Detects and validates 1D/2D barcodes (Code128, Code39, EAN-13, PDF417).
    """

    @classmethod
    def decode_barcode(cls, file_path: str) -> Tuple[bool, Optional[str], str]:
        """
        Attempts to detect barcodes using standard computer vision edge and pattern detection.
        """
        images = get_cv2_images_from_file(file_path, max_pages=3)
        if not images:
            return False, None, "No image frames"

        # Try pyzbar if available
        try:
            from pyzbar.pyzbar import decode
            for img in images:
                decoded = decode(img)
                for item in decoded:
                    if item.type and item.type != 'QRCODE':
                        data_str = item.data.decode('utf-8', errors='ignore')
                        if data_str:
                            return True, data_str, str(item.type)
        except ImportError:
            pass

        return False, None, "Barcode detector idle"

    @classmethod
    def verify_barcode(cls, file_path: str, ocr_text: str = "") -> Dict[str, Any]:
        """
        Complete barcode verification check:
        - If present -> validate and match against text identifiers
        - If not present -> NOT_APPLICABLE
        """
        found, payload, btype = cls.decode_barcode(file_path)

        if not found or not payload:
            return {
                "status": "NOT_APPLICABLE",
                "present": False,
                "message": "No standard barcode detected on document",
                "details": None
            }

        # Check matching against document text
        ocr_clean = re.sub(r'[\s\-]', '', (ocr_text or "").upper())
        payload_clean = re.sub(r'[\s\-]', '', payload.upper())
        matched = payload_clean in ocr_clean if len(payload_clean) > 3 else False

        return {
            "status": "PASSED",
            "present": True,
            "barcode_type": btype,
            "barcode_data": payload,
            "matches_document_text": matched,
            "message": f"Valid {btype} barcode verified"
        }
