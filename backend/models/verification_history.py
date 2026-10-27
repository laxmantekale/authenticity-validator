from datetime import datetime
from extensions import db

class VerificationHistory(db.Model):
    __tablename__ = "verification_history"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    verification_id = db.Column(db.Integer, db.ForeignKey("verifications.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    verification_source = db.Column(db.String(20), default="STUDENT", nullable=False, index=True) # 'STUDENT' | 'COLLEGE'
    document_name = db.Column(db.String(255), nullable=False)
    authentication_status = db.Column(db.String(50), nullable=False)
    verification_date = db.Column(db.DateTime, default=datetime.utcnow)
    report_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        doc_type = self.document.document_type if self.document else None
        doc_hash = self.document.file_hash if self.document else None
        ver_code = f"VER-{str(self.verification_id).zfill(5)}"
        
        return {
            "id": self.id,
            "verification_id": self.verification_id,
            "verification_code": ver_code,
            "student_id": self.student_id,
            "student_name": self.student.full_name if self.student else ("Direct College Verification" if self.verification_source == "COLLEGE" else "N/A"),
            "student_id_code": self.student.student_id if self.student else ("COLLEGE" if self.verification_source == "COLLEGE" else "N/A"),
            "college_id": self.college_id,
            "verification_source": self.verification_source,
            "document_id": self.document_id,
            "document_name": doc_type or self.document_name,
            "display_name": doc_type or self.document_name,
            "document_type": doc_type or "Academic Document",
            "file_hash": doc_hash,
            "authentication_status": self.authentication_status,
            "status": (
                "Authenticated" if self.authentication_status.upper() == "AUTHENTICATED"
                else "Suspicious" if self.authentication_status.upper() == "SUSPICIOUS"
                else "Not Verified" if self.authentication_status.upper() == "NOT_VERIFIED"
                else "Verification Failed" if self.authentication_status.upper() == "VERIFICATION_FAILED"
                else "In Progress" if self.authentication_status.upper() in ["PENDING", "IN_PROGRESS"]
                else self.authentication_status.replace("_", " ").title()
            ),
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "action_timestamp": self.verification_date.isoformat() if self.verification_date else None,
            "report_id": self.report_id,
            "details": (
                "Verification Passed" if self.authentication_status.upper() == "AUTHENTICATED"
                else "Verification Flagged (Suspicious)" if self.authentication_status.upper() == "SUSPICIOUS"
                else "Verification Inconclusive (Not Verified)" if self.authentication_status.upper() == "NOT_VERIFIED"
                else "Verification Failed" if self.authentication_status.upper() == "VERIFICATION_FAILED"
                else f"Verification {self.authentication_status.replace('_', ' ').title()}"
            )
        }
