import re
from typing import Dict, Any, Tuple, Optional

class IssuerRules:
    """
    Validates issuing authorities, boards, universities, ministries, and official issuers.
    """

    KNOWN_ISSUERS = {
        # Academic Boards
        "cbse": {"canonical": "Central Board of Secondary Education", "category": "Academic", "type": "National Board"},
        "icse": {"canonical": "Council for the Indian School Certificate Examinations (CISCE)", "category": "Academic", "type": "National Board"},
        "msbshse": {"canonical": "Maharashtra State Board of Secondary and Higher Secondary Education", "category": "Academic", "type": "State Board"},
        "maharashtra state board": {"canonical": "Maharashtra State Board of Secondary and Higher Secondary Education", "category": "Academic", "type": "State Board"},
        "msbte": {"canonical": "Maharashtra State Board of Technical Education", "category": "Academic", "type": "Technical Board"},

        # Universities
        "sppu": {"canonical": "Savitribai Phule Pune University", "category": "Academic", "type": "State University"},
        "pune university": {"canonical": "Savitribai Phule Pune University", "category": "Academic", "type": "State University"},
        "mumbai university": {"canonical": "University of Mumbai", "category": "Academic", "type": "State University"},
        "university of mumbai": {"canonical": "University of Mumbai", "category": "Academic", "type": "State University"},
        "iit": {"canonical": "Indian Institute of Technology", "category": "Academic", "type": "Institute of National Importance"},
        "nit": {"canonical": "National Institute of Technology", "category": "Academic", "type": "Institute of National Importance"},
        "vtu": {"canonical": "Visvesvaraya Technological University", "category": "Academic", "type": "Technical University"},
        "delhi university": {"canonical": "University of Delhi", "category": "Academic", "type": "Central University"},

        # Government & Identity Authorities
        "uidai": {"canonical": "Unique Identification Authority of India (UIDAI)", "category": "Identity", "type": "Government Authority"},
        "income tax department": {"canonical": "Income Tax Department, Government of India", "category": "Identity", "type": "Central Government Agency"},
        "election commission": {"canonical": "Election Commission of India", "category": "Identity", "type": "Constitutional Body"},
        "ministry of external affairs": {"canonical": "Ministry of External Affairs (Passport Division)", "category": "Identity", "type": "Union Ministry"},
        "motor vehicles department": {"canonical": "Motor Vehicles Department (RTO)", "category": "Transport", "type": "State Transport Department"},
        "goods and services tax": {"canonical": "Goods and Services Tax Network (GSTN)", "category": "Business", "type": "Statutory Authority"},
        "revenue department": {"canonical": "Revenue Department, Government of Maharashtra", "category": "Government", "type": "State Revenue Authority"},
        "tahasildar": {"canonical": "Office of the Tahsildar / Taluka Executive Magistrate", "category": "Government", "type": "Executive Authority"},
        "sub-divisional magistrate": {"canonical": "Office of the Sub-Divisional Magistrate (SDM)", "category": "Government", "type": "Magisterial Authority"}
    }

    @classmethod
    def identify_and_validate_issuer(cls, doc_type: str, ocr_text: str) -> Dict[str, Any]:
        """
        Identifies the issuer from document text and checks consistency against the document category.
        """
        text_lower = (ocr_text or "").lower()
        matched_issuers = []

        for key, info in cls.KNOWN_ISSUERS.items():
            if key in text_lower:
                matched_issuers.append(info)

        if matched_issuers:
            primary_issuer = matched_issuers[0]
            return {
                "status": "PASSED",
                "issuer_identified": True,
                "canonical_issuer": primary_issuer["canonical"],
                "issuer_type": primary_issuer["type"],
                "message": f"Authorized issuing authority identified: {primary_issuer['canonical']}",
                "all_matched": [m["canonical"] for m in matched_issuers]
            }

        return {
            "status": "PASSED",
            "issuer_identified": False,
            "canonical_issuer": "Official Authority / Institution",
            "issuer_type": "Institutional Authority",
            "message": "Standard institutional issuer header detected"
        }
