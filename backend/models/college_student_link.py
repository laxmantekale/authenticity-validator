from datetime import datetime
from extensions import db

class CollegeStudentLink(db.Model):
    __tablename__ = "college_student_links"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(20), default="PENDING", nullable=False, index=True)  # 'PENDING', 'ACCEPTED', 'REJECTED', 'UNLINKED', 'REMOVED'
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    unlinked_at = db.Column(db.DateTime, nullable=True)
    unlinked_by = db.Column(db.String(20), nullable=True)  # 'STUDENT', 'COLLEGE'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint("student_id", "college_id", name="uq_student_college"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "college_id": self.college_id,
            "status": self.status.lower(),
            "status_raw": self.status,
            "request_source": "portal",
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "unlinked_at": self.unlinked_at.isoformat() if self.unlinked_at else None,
            "unlinked_by": self.unlinked_by,
            "responded_at": (self.accepted_at or self.rejected_at).isoformat() if (self.accepted_at or self.rejected_at) else None,
            "student": self.student.to_dict() if self.student else None,
            "college": self.college.to_dict() if self.college else None
        }
