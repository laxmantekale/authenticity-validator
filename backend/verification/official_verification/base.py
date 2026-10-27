import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OfficialVerificationAdapter(ABC):
    """
    Abstract Base Class for official external/institutional verification adapters.
    All official verification adapters must implement can_handle and verify.
    """
    name: str = "Base Official Adapter"
    category: str = "general"

    @abstractmethod
    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        """Determines if this adapter can process the given document type and identifiers."""
        pass

    @abstractmethod
    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Performs official verification.
        Returns a dict with:
          - status: "PASSED" | "FAILED" | "UNAVAILABLE" | "NOT_APPLICABLE"
          - source: str
          - matched_record: Optional[Dict[str, Any]]
          - message: str
          - details: Dict[str, Any]
        """
        pass
