from datetime import datetime
from extensions import db

class Verification(db.Model):
    __tablename__ = "verifications"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Verification source: 'STUDENT' or 'COLLEGE'
    verification_source = db.Column(db.String(20), default="STUDENT", nullable=False, index=True)
    
    # Final Result: 'AUTHENTICATED', 'SUSPICIOUS', 'NOT_VERIFIED', 'VERIFICATION_FAILED', 'IN_PROGRESS'
    final_status = db.Column(db.String(30), nullable=False, index=True)
    
    # Modular verification signals
    ocr_status = db.Column(db.String(50), default="PASSED")
    qr_status = db.Column(db.String(50), default="NOT_APPLICABLE")
    forgery_status = db.Column(db.String(50), default="PASSED")
    signature_status = db.Column(db.String(50), default="NOT_APPLICABLE")
    stamp_status = db.Column(db.String(50), default="NOT_APPLICABLE")
    metadata_status = db.Column(db.String(50), default="PASSED")
    database_status = db.Column(db.String(50), default="NOT_APPLICABLE")
    
    confidence_score = db.Column(db.Float, default=0.95)
    verification_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    verification_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., VER-00001
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    history_records = db.relationship("VerificationHistory", backref="verification", cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="verification", cascade="all, delete-orphan")
    blockchain_records = db.relationship("BlockchainRecord", backref="verification")
    
    @property
    def overall_status(self):
        return self.final_status_clean

    @property
    def final_status_clean(self):
        if not self.final_status:
            return "Pending"
        st = str(self.final_status).upper()
        if st == "AUTHENTICATED":
            return "Authenticated"
        elif st == "SUSPICIOUS":
            return "Suspicious"
        elif st == "NOT_VERIFIED":
            return "Not Verified"
        elif st == "VERIFICATION_FAILED":
            return "Verification Failed"
        elif st == "NOT_AUTHENTICATED":
            return "Not Authenticated"
        elif st in ["IN_PROGRESS", "PENDING"]:
            return "In Progress"
        return self.final_status.replace("_", " ").title()

    @property
    def sha256_hash(self):
        return self.document.file_hash if self.document else ""

    def _format_result(self, val):
        if not val or str(val).upper() in ["NOT_APPLICABLE", "SKIPPED"]:
            return "NOT_APPLICABLE"
        elif str(val).upper() in ["PASSED", "SUCCESS", "AUTHENTICATED"]:
            return "SUCCESS"
        return "FAILED"

    def to_dict(self):
        b_rec = self.blockchain_records[-1] if self.blockchain_records else None
        return {
            "id": self.id,
            "verification_id": self.verification_id,
            "document_id": self.document_id,
            "student_id": self.student_id,
            "college_id": self.college_id,
            "verification_source": self.verification_source,
            "document_title": self.document.document_title if self.document else "Document",
            "document_name": self.document.original_filename if self.document else "Document",
            "document_type": self.document.document_type if self.document else "Academic Document",
            "overall_status": self.final_status_clean,
            "final_status": self.final_status,
            "confidence_score": self.confidence_score,
            "sha256_hash": self.sha256_hash,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "blockchain_tx_hash": b_rec.blockchain_tx_hash if b_rec else None,
            "results": {
                "ocr": self._format_result(self.ocr_status),
                "qr": self._format_result(self.qr_status),
                "forgery": self._format_result(self.forgery_status),
                "signature": self._format_result(self.signature_status),
                "stamp": self._format_result(self.stamp_status),
                "metadata": self._format_result(self.metadata_status)
            },
            "signals": {
                "ocr_status": self.ocr_status,
                "qr_status": self.qr_status,
                "forgery_status": self.forgery_status,
                "signature_status": self.signature_status,
                "stamp_status": self.stamp_status,
                "metadata_status": self.metadata_status,
                "database_status": self.database_status
            }
        }
