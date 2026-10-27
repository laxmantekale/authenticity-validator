import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class EmploymentOfficialAdapter(OfficialVerificationAdapter):
    name = "Employer & EPFO Verification Adapter"
    category = "employment"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        emp_types = ["Salary Slip", "Pay Slip", "Experience Certificate", "Relieving Letter", "Offer Letter", "Appointment Letter"]
        return any(t.lower() in doc_type.lower() for t in emp_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        emp_id = identifiers.get("employee_id") or identifiers.get("uan")
        return {
            "status": "UNAVAILABLE",
            "source": "EPFO Unified Portal / Corporate HR Verification System",
            "matched_record": None,
            "message": "Corporate HR / EPFO API bridge is not configured.",
            "details": {"identifier_parsed": emp_id or "None", "reason": "No live corporate integration"}
        }
