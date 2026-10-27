from extensions import db
from models.student import Student
from models.document import Document
from models.college_student_link import CollegeStudentLink
from models.verification import Verification

class StudentService:
    @staticmethod
    def get_profile(user_id):
        student = Student.query.filter_by(user_id=user_id).first()
        return student

    @staticmethod
    def update_profile(user_id, full_name, mobile):
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return None, "Student profile not found."
        if full_name:
            student.full_name = full_name
        if mobile:
            student.mobile = mobile
        db.session.commit()
        return student, None

    @staticmethod
    def get_dashboard_stats(user_id):
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return {}

        docs = Document.query.filter_by(student_id=student.id, is_deleted=False).all()
        total_docs = len(docs)
        doc_ids = [d.id for d in docs]

        auth_docs = 0
        pending_count = 0
        not_verified_count = 0

        if doc_ids:
            for d in docs:
                latest_v = Verification.query.filter_by(document_id=d.id)\
                    .order_by(Verification.verification_date.desc(), Verification.id.desc()).first()
                if latest_v:
                    st = (latest_v.final_status or "").upper()
                    if st == "AUTHENTICATED":
                        auth_docs += 1
                    elif st in ["PENDING", "IN_PROGRESS"]:
                        pending_count += 1
                    else:
                        not_verified_count += 1
                else:
                    pending_count += 1

        pending_or_not_verified = pending_count + not_verified_count

        if doc_ids:
            total_history = VerificationHistory.query.filter(
                VerificationHistory.student_id == student.id,
                VerificationHistory.document_id.in_(doc_ids)
            ).count()
            recent_verifications = Verification.query.filter(
                Verification.student_id == student.id,
                Verification.document_id.in_(doc_ids)
            ).order_by(Verification.verification_date.desc(), Verification.id.desc()).limit(5).all()
        else:
            total_history = 0
            recent_verifications = []

        linked_colleges = CollegeStudentLink.query.filter_by(
            student_id=student.id,
            status='ACCEPTED'
        ).count()

        return {
            "student": student.to_dict(),
            "stats": {
                "total_documents": total_docs,
                "total_verifications": total_history,
                "verified_documents": auth_docs,
                "authenticated": auth_docs,
                "authenticated_documents": auth_docs,
                "pending_not_verified": pending_or_not_verified,
                "pending_documents": pending_count,
                "pending": pending_count,
                "not_verified": not_verified_count,
                "rejected_documents": not_verified_count,
                "total_history": total_history,
                "linked_colleges": linked_colleges
            },
            "recent_verifications": [v.to_dict() for v in recent_verifications]
        }
