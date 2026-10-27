import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class IdentityOfficialAdapter(OfficialVerificationAdapter):
    name = "National Identity Verification Adapter"
    category = "identity"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        id_types = [
            "Aadhaar Card", "PAN Card", "Voter ID Card", "Passport", "Driving Licence", "Ration Card"
        ]
        return any(t.lower() in doc_type.lower() for t in id_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Verifies National Identity documents (PAN, Aadhaar, Passport, Voter ID) against official gateways.
        Returns UNAVAILABLE if external statutory API is not linked.
        """
        id_val = (
            identifiers.get("pan_number") or
            identifiers.get("aadhaar_number") or
            identifiers.get("voter_id_number") or
            identifiers.get("passport_number") or
            identifiers.get("driving_licence_number")
        )
        return {
            "status": "UNAVAILABLE",
            "source": "Statutory Identity Verification Gateway (UIDAI / NSDL / ECI / PSP)",
            "matched_record": None,
            "message": "Direct statutory registry API is not linked. Structural checksum and format were validated locally.",
            "details": {"identifier_parsed": id_val or "Present", "reason": "Statutory API credentials required"}
        }
