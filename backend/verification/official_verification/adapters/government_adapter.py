import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class GovernmentOfficialAdapter(OfficialVerificationAdapter):
    name = "State Government & Revenue Portal Adapter"
    category = "government"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        govt_types = [
            "Domicile Certificate", "Income Certificate", "Caste Certificate",
            "Non-Creamy Layer Certificate", "Birth Certificate", "Death Certificate",
            "Disability Certificate", "Gazette Notification", "7/12 Extract", "Property Card"
        ]
        return any(t.lower() in doc_type.lower() for t in govt_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Verifies government issued certificates against state revenue/portal gateways (e.g. Aaple Sarkar).
        """
        app_no = identifiers.get("application_number") or identifiers.get("certificate_number") or identifiers.get("barcode_number")
        return {
            "status": "UNAVAILABLE",
            "source": "State Public Services / MahaOnline Registry",
            "matched_record": None,
            "message": "Government portal verification gateway (Aaple Sarkar / MahaOnline API) is currently disconnected.",
            "details": {"identifier_checked": app_no or "None", "reason": "No active API bridge"}
        }
