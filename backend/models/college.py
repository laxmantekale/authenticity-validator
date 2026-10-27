import secrets
from datetime import datetime
from extensions import db

class College(db.Model):
    __tablename__ = "colleges"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    college_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., NIT101
    college_name = db.Column(db.String(255), nullable=False)
    official_email = db.Column(db.String(191), nullable=False)
    mobile = db.Column(db.String(25), nullable=False)
    address = db.Column(db.Text, nullable=False)
    qr_token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    secure_link_token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_links = db.relationship("CollegeStudentLink", backref="college", cascade="all, delete-orphan")
    documents = db.relationship("Document", backref="college")
    verifications = db.relationship("Verification", backref="college")
    verification_histories = db.relationship("VerificationHistory", backref="college")
    
    # Backward compatibility properties
    @property
    def college_code(self):
        return self.college_id

    @property
    def contact_number(self):
        return self.mobile

    @property
    def secure_link_slug(self):
        return self.secure_link_token
        
    @staticmethod
    def generate_token():
        return secrets.token_hex(16)
        
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "college_id": self.college_id,
            "college_code": self.college_id,
            "college_name": self.college_name,
            "email": self.official_email,
            "official_email": self.official_email,
            "mobile": self.mobile,
            "contact_number": self.mobile,
            "address": self.address,
            "qr_token": self.qr_token,
            "secure_link_token": self.secure_link_token,
            "secure_link_slug": self.secure_link_token,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
