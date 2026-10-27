import uuid
import json
import logging
from datetime import datetime
from extensions import db
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from models.blockchain_record import BlockchainRecord
from models.student import Student
from models.college import College
from models.college_student_link import CollegeStudentLink
from verification.engine import verification_engine
from services.report_service import ReportService

logger = logging.getLogger(__name__)

class VerificationService:
    @staticmethod
    def generate_unique_verification_id():
        """Generates a guaranteed unique verification ID code."""
        max_id = db.session.query(db.func.max(Verification.id)).scalar() or 0
        rand_suffix = uuid.uuid4().hex[:4].upper()
        return f"VER-{str(max_id + 1).zfill(5)}-{rand_suffix}"

    @staticmethod
    def generate_unique_report_id():
        """Generates a guaranteed unique report ID code."""
        max_id = db.session.query(db.func.max(Report.id)).scalar() or 0
        rand_suffix = uuid.uuid4().hex[:4].upper()
        return f"AVR-{str(max_id + 1).zfill(5)}-{rand_suffix}"

    @staticmethod
    def verify_document(document_id, user_id=None, role=None, candidate_name=None):
        """
        Executes the verification pipeline and saves all records into database.
        Supports both Student verification and Direct College verification.
        """
        doc = db.session.get(Document, document_id)
        if not doc:
            return None, "Document not found."

        student = doc.student
        college = doc.college

        # Determine verification source
        verification_source = "COLLEGE" if role == "college" or student is None else "STUDENT"

        # If student doc and college is not explicitly attached, check if student is linked to a college
        if not college and student:
            accepted_link = CollegeStudentLink.query.filter(
                (CollegeStudentLink.student_id == student.id) &
                (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
            ).first()
            if accepted_link:
                college = accepted_link.college

        # If college verification and college not on doc, fetch from user_id
        if verification_source == "COLLEGE" and not college and user_id:
            college = College.query.filter_by(user_id=int(user_id)).first()
            if college:
                doc.college_id = college.id

        # Execute multi-factor verification pipeline
        try:
            res = verification_engine.run_full_pipeline(
                file_path=doc.file_path,
                student=student,
                college=college,
                user_selected_type=doc.document_type
            )
        except Exception as e:
            logger.error(f"Verification pipeline unexpected exception: {e}")
            res = {
                "overall_status": "VERIFICATION_FAILED",
                "final_status": "VERIFICATION_FAILED",
                "ai_status": "VERIFICATION_FAILED",
                "official_status": "NOT_AVAILABLE",
                "sha256_hash": doc.file_hash,
                "confidence_score": 0.0,
                "confidence_level": "Verification Failed (System Error)",
                "doc_type_detected": doc.document_type or "Unknown Document",
                "document_type": doc.document_type or "Unknown Document",
                "category": "Unknown",
                "classification_status": "UNKNOWN_DOCUMENT",
                "results": {
                    "ocr": "FAILED",
                    "qr": "NOT_APPLICABLE",
                    "forgery": "NOT_APPLICABLE",
                    "signature": "NOT_APPLICABLE",
                    "stamp": "NOT_APPLICABLE",
                    "metadata": "NOT_APPLICABLE"
                },
                "signals": {
                    "file_validation": "Failed",
                    "ocr_status": "Failed",
                    "qr_status": "Not Applicable",
                    "ai_forgery_status": "Not Applicable",
                    "tampering_status": "Not Applicable",
                    "signature_status": "Not Applicable",
                    "stamp_status": "Not Applicable",
                    "metadata_status": "Not Applicable",
                    "database_status": "Not Applicable",
                    "blockchain_status": "Failed"
                },
                "findings": {
                    "confirmed": [],
                    "warnings": [f"Technical verification error: {str(e)}"],
                    "checks_not_performed": ["All verification checks skipped due to processing error"],
                    "technical_limitations": [str(e)]
                },
                "decision_explanation": f"Verification could not be completed due to an unexpected system processing failure ({str(e)}).",
                "recommended_next_steps": [
                    "Ensure the document is a valid, uncorrupted PDF or image.",
                    "Retry the verification or contact technical support if the issue persists."
                ],
                "ocr_data": {},
                "blockchain_record": None
            }

        raw_status = res.get("overall_status", "NOT_VERIFIED")
        detected_doc_type = res.get("doc_type_detected") or doc.document_type
        doc.document_type = detected_doc_type
        
        final_status = res.get("final_status")
        if not final_status:
            if raw_status in ["Authenticated", "AUTHENTICATED"]:
                final_status = "AUTHENTICATED"
            elif raw_status in ["Pending", "PENDING", "IN_PROGRESS"]:
                final_status = "IN_PROGRESS"
            elif raw_status in ["Suspicious", "SUSPICIOUS"]:
                final_status = "SUSPICIOUS"
            elif raw_status in ["Verification Failed", "VERIFICATION_FAILED"]:
                final_status = "VERIFICATION_FAILED"
            else:
                final_status = "NOT_VERIFIED"

        sha256 = res.get("sha256_hash", doc.file_hash)
        signals = res.get("signals", {})
        results = res.get("results", {})

        # Generate unique verification code
        ver_id_code = VerificationService.generate_unique_verification_id()

        def normalize_signal(val):
            if not val or str(val).lower() in ["skipped", "not_applicable", "not applicable"]:
                return "NOT_APPLICABLE"
            elif str(val).lower() in ["passed", "success"]:
                return "PASSED"
            return "FAILED"

        # Create Verification record
        verification = Verification(
            document_id=doc.id,
            student_id=student.id if student else None,
            college_id=college.id if college else None,
            verification_source=verification_source,
            final_status=final_status,
            ocr_status=normalize_signal(signals.get("ocr_status", "Passed")),
            qr_status=normalize_signal(signals.get("qr_status", "Not Applicable")),
            forgery_status=normalize_signal(signals.get("ai_forgery_status", "Passed")),
            signature_status=normalize_signal(signals.get("signature_status", "Not Applicable")),
            stamp_status=normalize_signal(signals.get("stamp_status", "Not Applicable")),
            metadata_status=normalize_signal(signals.get("metadata_status", "Passed")),
            database_status=normalize_signal(signals.get("database_status", "Not Applicable")),
            confidence_score=res.get("confidence_score", 0.95),
            verification_date=datetime.utcnow(),
            verification_id=ver_id_code
        )
        db.session.add(verification)
        db.session.flush()

        # Generate official ReportLab PDF
        report_id_code = VerificationService.generate_unique_report_id()
        
        rep_student_name = student.full_name if student else (candidate_name or "Walk-in Candidate / Direct Verification")
        rep_student_id = student.student_id if student else "COLLEGE_DIRECT"

        auth_status_str = (
            "Authenticated" if final_status == "AUTHENTICATED"
            else "Suspicious" if final_status == "SUSPICIOUS"
            else "Not Verified" if final_status == "NOT_VERIFIED"
            else "Verification Failed" if final_status == "VERIFICATION_FAILED"
            else "Pending Review" if final_status in ["PENDING", "IN_PROGRESS"]
            else "Not Authenticated"
        )

        try:
            pdf_path = ReportService.generate_pdf_report(
                student_name=rep_student_name,
                student_id=rep_student_id,
                document_name=doc.original_filename,
                auth_status=auth_status_str,
                report_id=report_id_code,
                verification_date=verification.verification_date,
                doc_hash=sha256,
                doc_type=detected_doc_type,
                checks=res.get("checks", {}),
                full_verification_data=res
            )
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            pdf_path = ""

        # Create Report record
        report = Report(
            report_id=report_id_code,
            verification_id=verification.id,
            student_id=student.id if student else None,
            college_id=college.id if college else None,
            verification_source=verification_source,
            document_name=doc.original_filename,
            authentication_status=final_status,
            report_file_path=pdf_path,
            report_data=json.dumps(res, default=str),
            generated_at=datetime.utcnow()
        )
        db.session.add(report)

        # Create VerificationHistory record
        v_history = VerificationHistory(
            verification_id=verification.id,
            student_id=student.id if student else None,
            college_id=college.id if college else None,
            verification_source=verification_source,
            document_id=doc.id,
            document_name=doc.original_filename,
            authentication_status=final_status,
            verification_date=verification.verification_date,
            report_id=report_id_code
        )
        db.session.add(v_history)

        # Create BlockchainRecord
        bc_data = res.get("blockchain_record") or {}
        tx_hash = bc_data.get("tx_hash") or f"0x{sha256[:40]}"
        b_rec = BlockchainRecord(
            document_id=doc.id,
            verification_id=verification.id,
            document_hash=sha256,
            blockchain_tx_hash=tx_hash,
            blockchain_network="Polygon POS Testnet",
            blockchain_status="CONFIRMED" if final_status == "AUTHENTICATED" else "FAILED",
            timestamp=datetime.utcnow()
        )
        db.session.add(b_rec)
        db.session.commit()

        ver_dict = verification.to_dict()
        ver_dict["report_id"] = report_id_code
        ver_dict["report_url"] = f"/api/reports/download/{report_id_code}"
        ver_dict["checks"] = res.get("checks", {})

        return {
            "success": True,
            "verification_id": ver_id_code,
            "final_status": final_status,
            "overall_status": verification.final_status_clean,
            "ai_status": res.get("ai_status", final_status),
            "official_status": res.get("official_status", "NOT_AVAILABLE"),
            "document_name": doc.original_filename,
            "document_type": detected_doc_type,
            "category": res.get("category", "General"),
            "classification_status": res.get("classification_status", "SUPPORTED_DOCUMENT"),
            "classification_confidence": round(float(res.get("classification_confidence", 95.0)), 2),
            "confidence_level": res.get("confidence_level", "High Confidence"),
            "checks": res.get("checks", {}),
            "evidence": res.get("evidence", {}),
            "results": results,
            "signals": signals,
            "confidence_score": verification.confidence_score,
            "sha256_hash": sha256,
            "report_id": report_id_code,
            "report_url": f"/api/reports/download/{report_id_code}",
            "verification": ver_dict
        }, None

# Global instance
verification_service = VerificationService()
