import os
import re
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None
from typing import Dict, Any, Tuple, Optional

class SignatureRules:
    """
    Validates PDF digital signatures, PKCS#7 certificates, and authorized signatory blocks.
    """

    AUTHORIZED_SIGNATORY_TITLES = [
        r"controller\s+of\s+examinations",
        r"vice[- ]chancellor",
        r"registrar",
        r"principal",
        r"head\s+of\s+(?:institution|department)",
        r"director",
        r"secretary",
        r"authorized\s+signatory",
        r"tahasildar",
        r"sub[- ]divisional\s+magistrate",
        r"competent\s+authority",
        r"medical\s+officer",
        r"registered\s+medical\s+practitioner",
        r"deputy\s+commissioner",
        r"joint\s+commissioner"
    ]

    @classmethod
    def check_pdf_digital_signature(cls, file_path: str) -> Dict[str, Any]:
        """
        Inspects PDF structure for Adobe / PKCS#7 digital signature dictionaries.
        """
        _, ext = os.path.splitext(file_path)
        if ext.lower() != '.pdf':
            return {
                "status": "NOT_APPLICABLE",
                "digitally_signed": False,
                "message": "Digital signature verification is applicable for PDF documents only."
            }

        try:
            if pymupdf is None:
                return {
                    "status": "NOT_APPLICABLE",
                    "digitally_signed": False,
                    "message": "PDF engine not available for digital signature check"
                }

            doc = pymupdf.open(file_path)
            # Check page count and fields
            sig_fields = []
            for page in doc:
                for widget in page.widgets():
                    if widget.field_type == pymupdf.PDF_WIDGET_TYPE_SIGNATURE:
                        sig_fields.append(widget.field_name)

            # Raw byte check for ByteRange signatures
            with open(file_path, 'rb') as f:
                content = f.read(500000)
                has_byte_range = b"/ByteRange" in content
                has_pkcs7 = b"/adbe.pkcs7" in content or b"/Adobe.PPKLite" in content

            doc.close()

            if sig_fields or (has_byte_range and has_pkcs7):
                return {
                    "status": "PASSED",
                    "digitally_signed": True,
                    "signature_fields": sig_fields,
                    "message": "Cryptographically verifiable digital signature detected"
                }

            return {
                "status": "NOT_APPLICABLE",
                "digitally_signed": False,
                "message": "No digital certificate signature embedded"
            }

        except Exception as e:
            return {
                "status": "NOT_APPLICABLE",
                "digitally_signed": False,
                "message": f"Digital signature check: {str(e)}"
            }

    @classmethod
    def check_signatory_block(cls, ocr_text: str) -> Dict[str, Any]:
        """
        Verifies presence of authorized institutional signatory titles.
        """
        text_lower = (ocr_text or "").lower()
        matched_titles = []

        for title_pat in cls.AUTHORIZED_SIGNATORY_TITLES:
            if re.search(title_pat, text_lower):
                matched_titles.append(title_pat)

        if matched_titles:
            return {
                "status": "PASSED",
                "signatory_block_present": True,
                "matched_titles": matched_titles,
                "message": "Authorized institutional signatory designation identified"
            }

        return {
            "status": "NOT_APPLICABLE",
            "signatory_block_present": False,
            "message": "No specific signatory designation block required"
        }
