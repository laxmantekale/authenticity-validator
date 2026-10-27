from models.verification_history import VerificationHistory
from models.document import Document
from models.student import Student
from models.college import College

class HistoryService:
    @staticmethod
    def get_student_history(student_user_id):
        student = Student.query.filter_by(user_id=student_user_id).first()
        if not student:
            return []
        records = VerificationHistory.query.join(Document, VerificationHistory.document_id == Document.id).filter(
            VerificationHistory.student_id == student.id,
            VerificationHistory.verification_source == "STUDENT",
            Document.is_deleted == False
        ).order_by(VerificationHistory.verification_date.desc()).all()
        return [r.to_dict() for r in records]

    @staticmethod
    def get_college_history(college_user_id):
        college = College.query.filter_by(user_id=college_user_id).first()
        if not college:
            return []
        records = VerificationHistory.query.join(Document, VerificationHistory.document_id == Document.id).filter(
            VerificationHistory.college_id == college.id,
            VerificationHistory.verification_source == "COLLEGE",
            Document.is_deleted == False
        ).order_by(VerificationHistory.verification_date.desc()).all()
        return [r.to_dict() for r in records]
