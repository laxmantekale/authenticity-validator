import logging
from typing import Dict, Any, Optional
from verification.official_verification.base import OfficialVerificationAdapter

logger = logging.getLogger(__name__)

class UniversityOfficialAdapter(OfficialVerificationAdapter):
    name = "Institutional University Registry Adapter"
    category = "academic"

    def can_handle(self, doc_type: str, issuer_info: Dict[str, Any], identifiers: Dict[str, Any]) -> bool:
        academic_types = [
            "University Degree Certificate", "Degree Certificate", "Provisional Degree Certificate",
            "University Marksheet", "Semester Marksheet", "Consolidated Marksheet", "Transcript",
            "Academic Transcript", "Passing Certificate", "Migration Certificate", "Bonafide Certificate",
            "Leaving Certificate", "Transfer Certificate", "College ID Card"
        ]
        return any(t.lower() in doc_type.lower() for t in academic_types)

    def verify(
        self,
        doc_type: str,
        identifiers: Dict[str, Any],
        ocr_data: Dict[str, Any],
        student: Optional[Any] = None,
        college: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Verifies student academic credentials against institutional records if student/college links exist.
        Otherwise returns UNAVAILABLE without fabricating records.
        """
        extracted_text = ocr_data.get("raw_text", "")
        roll_no = identifiers.get("roll_number") or identifiers.get("seat_number") or identifiers.get("registration_number")
        prn_no = identifiers.get("prn_number") or identifiers.get("enrollment_number")

        # Check local student / college database linkage
        if student and student.student_id:
            db_id = student.student_id.upper().strip()
            # If student id is present in the document text or matching identifiers
            if db_id in extracted_text.upper() or (roll_no and roll_no.upper() in db_id) or (prn_no and prn_no.upper() in db_id):
                return {
                    "status": "PASSED",
                    "source": "Institutional Academic Records System",
                    "matched_record": {
                        "student_id": student.student_id,
                        "full_name": student.full_name,
                        "college_name": college.college_name if college else "Registered Institution"
                    },
                    "message": f"Document matched registered student record ({student.student_id}) in institutional database.",
                    "details": {"verified_via": "Local Institution Registry", "matched_field": "student_id"}
                }

        return {
            "status": "UNAVAILABLE",
            "source": "Institutional Academic Records System",
            "matched_record": None,
            "message": "University live API endpoint or institutional registry connection is not configured.",
            "details": {"reason": "No direct external API endpoint active for this institution"}
        }
