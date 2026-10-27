from typing import Dict, Any, List
from verification.registry import DocumentTypeRegistry


class DocumentRules:
    """
    Defines document profiles, field requirements, and expected attributes across all categories.
    Bridges to DocumentTypeRegistry.
    """

    PROFILES = DocumentTypeRegistry._REGISTRY

    @classmethod
    def get_profile(cls, doc_type: str) -> Dict[str, Any]:
        return DocumentTypeRegistry.get_profile(doc_type)

    @classmethod
    def list_all_types(cls) -> List[str]:
        return DocumentTypeRegistry.list_all_types()

    @classmethod
    def get_category(cls, doc_type: str) -> str:
        return DocumentTypeRegistry.get_category(doc_type)
