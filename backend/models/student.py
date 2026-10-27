from datetime import datetime
from extensions import db

class Student(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., STU001
    full_name = db.Column(db.String(191), nullable=False)
    mobile = db.Column(db.String(25), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    college_links = db.relationship("CollegeStudentLink", backref="student", cascade="all, delete-orphan")
    documents = db.relationship("Document", backref="student", cascade="all, delete-orphan")
    verifications = db.relationship("Verification", backref="student", cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="student", cascade="all, delete-orphan")
    verification_histories = db.relationship("VerificationHistory", backref="student", cascade="all, delete-orphan")
    
    # Backward compatibility properties
    @property
    def student_id_code(self):
        return self.student_id

    @property
    def mobile_number(self):
        return self.mobile
        
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.user.email if self.user else None,
            "name": self.full_name,
            "full_name": self.full_name,
            "student_id": self.student_id,
            "student_id_code": self.student_id,
            "mobile": self.mobile,
            "mobile_number": self.mobile,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
