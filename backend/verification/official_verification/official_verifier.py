import logging
from typing import Dict, Any, Optional, List
from verification.official_verification.base import OfficialVerificationAdapter
from verification.official_verification.adapters.university_adapter import UniversityOfficialAdapter
from verification.official_verification.adapters.board_adapter import BoardOfficialAdapter
from verification.official_verification.adapters.government_adapter import GovernmentOfficialAdapter
from verification.official_verification.adapters.identity_adapter import IdentityOfficialAdapter
from verification.official_verification.adapters.transport_adapter import TransportOfficialAdapter
from verification.official_verification.adapters.gst_adapter import GstOfficialAdapter
from verification.official_verification.adapters.banking_adapter import BankingOfficialAdapter
from verification.official_verification.adapters.employment_adapter import EmploymentOfficialAdapter

logger = logging.getLogger(__name__)

class OfficialVerifier:
    """
    Central dispatcher for all official external and institutional verification adapters.
    """
    def __init__(self):
        self.adapters: List[OfficialVerificationAdapter] = [
            UniversityOfficialAdapter(),
            BoardOfficialAdapter(),
            GovernmentOfficialAdapter(),
            IdentityOfficialAdapter(),
            TransportOfficialAdapter(),
            GstOfficialAdapter(),
            BankingOfficialAdapter(),
            EmploymentOfficialAdapter()
        ]

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        issuer_info: Optional[Dict[str, Any]] = None,
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes official verification against known adapters.
        """
        if not doc_type or doc_type == "Unknown Document":
            return {
                "status": "NOT_APPLICABLE",
                "source": "None",
                "message": "Official verification not applicable for unknown document format.",
                "matched_record": None,
                "details": {}
            }

        issuer_info = issuer_info or {}
        
        # Try finding a matching adapter
        for adapter in self.adapters:
            try:
                if adapter.can_handle(doc_type, issuer_info, identifiers):
                    res = adapter.verify(
                        doc_type=doc_type,
                        identifiers=identifiers,
                        ocr_data=ocr_data,
                        student=student,
                        college=college
                    )
                    return res
            except Exception as e:
                logger.error(f"Error running adapter {adapter.name}: {e}")

        # Fallback if no specific adapter handles this type
        return {
            "status": "UNAVAILABLE",
            "source": "External Official Database",
            "message": "Official verification registry not configured for this specific document category.",
            "matched_record": None,
            "details": {}
        }

official_verifier = OfficialVerifier()
