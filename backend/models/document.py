from datetime import datetime
from extensions import db

class Document(db.Model):
    __tablename__ = "documents"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True, index=True)
    document_type = db.Column(db.String(100), nullable=False, index=True)  # '10th Marksheet', '12th Marksheet', etc.
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA-256
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft deletion flags to ensure verification history and records are preserved
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    verifications = db.relationship("Verification", backref="document", cascade="all, delete-orphan")
    blockchain_records = db.relationship("BlockchainRecord", backref="document")
    verification_history = db.relationship("VerificationHistory", backref="document", cascade="all, delete-orphan")
    
    @property
    def document_title(self):
        return self.document_type if self.document_type and self.document_type.strip() else "Academic Document"
        
    def to_dict(self):
        latest_verification = self.verifications[-1] if self.verifications else None
        latest_report = latest_verification.reports[-1] if (latest_verification and latest_verification.reports) else None
        
        display_name = self.document_type if self.document_type and self.document_type.strip() else "Academic Document"
        
        return {
            "id": self.id,
            "student_id": self.student_id,
            "college_id": self.college_id,
            "name": display_name,
            "display_name": display_name,
            "document_title": display_name,
            "document_type": self.document_type or "Academic Document",
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "verification_status": latest_verification.final_status_clean if latest_verification else "Not Verified",
            "status": latest_verification.final_status_clean if latest_verification else "Not Verified",
            "final_status": latest_verification.final_status if latest_verification else "NOT_VERIFIED",
            "latest_status": latest_verification.final_status_clean if latest_verification else "Not Verified",
            "latest_verification_id": latest_verification.id if latest_verification else None,
            "verification_id": latest_verification.id if latest_verification else None,
            "verification_code": latest_verification.verification_id if latest_verification else None,
            "verification_date": latest_verification.verification_date.isoformat() if latest_verification and latest_verification.verification_date else None,
            "report_id": latest_report.report_id if latest_report else None,
            "report_id_code": latest_report.report_id if latest_report else None,
            "has_report": latest_report is not None,
            "view_url": f"/api/documents/{self.id}/view",
            "report_url": f"/api/reports/view/{latest_report.report_id}" if latest_report else None,
            "report_download_url": f"/api/reports/download/{latest_report.report_id}" if latest_report else None
        }
