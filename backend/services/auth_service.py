from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from utils.security import hash_password, check_password
import uuid

class AuthService:
    @staticmethod
    def register_student(email, password, full_name, mobile):
        if User.query.filter_by(email=email).first():
            return None, "Email address is already registered."

        user = User(
            email=email,
            password_hash=hash_password(password),
            role='student'
        )
        db.session.add(user)
        db.session.flush()

        student_code = f"STU{str(uuid.uuid4().int)[:6]}"
        student = Student(
            user_id=user.id,
            student_id=student_code,
            full_name=full_name,
            mobile=mobile
        )
        db.session.add(student)
        db.session.commit()
        return user, None

    @staticmethod
    def register_college(email, password, college_name, college_code, mobile, address):
        if User.query.filter_by(email=email).first():
            return None, "Email address is already registered."

        user = User(
            email=email,
            password_hash=hash_password(password),
            role='college'
        )
        db.session.add(user)
        db.session.flush()

        qr_tok = f"qr_{uuid.uuid4().hex[:16]}"
        link_tok = f"lnk_{uuid.uuid4().hex[:16]}"

        college = College(
            user_id=user.id,
            college_id=college_code.upper(),
            college_name=college_name,
            official_email=email,
            mobile=mobile,
            address=address,
            qr_token=qr_tok,
            secure_link_token=link_tok
        )
        db.session.add(college)
        db.session.commit()
        return user, None

    @staticmethod
    def authenticate(email, password, expected_role=None):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password(password, user.password_hash):
            return None, "Invalid email or password."
        if expected_role and user.role != expected_role:
            return None, f"Account does not have {expected_role} access privileges."
        return user, None
