import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class TransportOfficialAdapter(OfficialVerificationAdapter):
    name = "Transport Department & Parivahan Adapter"
    category = "transport"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        transport_types = [
            "Vehicle Registration Certificate", "RC Book", "Driving Licence", "Pollution Under Control Certificate", "PUC Certificate"
        ]
        return any(t.lower() in doc_type.lower() for t in transport_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        reg_no = identifiers.get("rc_number") or identifiers.get("driving_licence_number")
        return {
            "status": "UNAVAILABLE",
            "source": "Parivahan Sewa / Vahan-Sarathi Database",
            "matched_record": None,
            "message": "Parivahan / MoRTH national database connection is not active.",
            "details": {"identifier_parsed": reg_no or "None", "reason": "No active API bridge"}
        }
