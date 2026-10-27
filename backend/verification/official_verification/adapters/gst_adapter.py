import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class GstOfficialAdapter(OfficialVerificationAdapter):
    name = "GSTN / CBIC Portal Adapter"
    category = "business"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        gst_types = ["GST Registration Certificate", "GST Certificate", "Udyam Registration Certificate", "Certificate of Incorporation"]
        return any(t.lower() in doc_type.lower() for t in gst_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        gstin = identifiers.get("gstin")
        return {
            "status": "UNAVAILABLE",
            "source": "GSTN Official Portal / MCA21 Registry",
            "matched_record": None,
            "message": "GSTN / MCA21 direct verification gateway is not configured.",
            "details": {"gstin_parsed": gstin or "None", "reason": "No live API endpoint"}
        }
