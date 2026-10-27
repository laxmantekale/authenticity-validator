from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'STUDENT' or 'COLLEGE'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    college_profile = db.relationship("College", backref="user", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        profile_data = {}
        if self.role.upper() == "STUDENT" and self.student_profile:
            profile_data = self.student_profile.to_dict()
        elif self.role.upper() == "COLLEGE" and self.college_profile:
            profile_data = self.college_profile.to_dict()
            
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.lower(),
            "role_raw": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "profile": profile_data
        }
