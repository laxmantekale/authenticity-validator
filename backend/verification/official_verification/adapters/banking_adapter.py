import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class BankingOfficialAdapter(OfficialVerificationAdapter):
    name = "Core Banking & Financial Registry Adapter"
    category = "financial"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        fin_types = ["Bank Statement", "Fee Receipt", "Tuition Fee Receipt", "Scholarship Sanction Letter", "Loan Sanction Letter"]
        return any(t.lower() in doc_type.lower() for t in fin_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        acc_no = identifiers.get("account_number") or identifiers.get("transaction_id")
        return {
            "status": "UNAVAILABLE",
            "source": "Core Banking System / Open Banking API",
            "matched_record": None,
            "message": "Financial institution Open Banking API is not linked for live account reconciliation.",
            "details": {"identifier_parsed": acc_no or "None", "reason": "No live banking API gateway"}
        }
