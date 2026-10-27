from extensions import db
from models.college import College
from models.college_student_link import CollegeStudentLink
from models.document import Document
from models.verification import Verification
from utils.qr_utils import generate_qr_base64

class CollegeService:
    @staticmethod
    def get_profile(user_id):
        return College.query.filter_by(user_id=user_id).first()

    @staticmethod
    def update_profile(user_id, college_name, mobile, address):
        college = College.query.filter_by(user_id=user_id).first()
        if not college:
            return None, "College profile not found."
        if college_name:
            college.college_name = college_name
        if mobile:
            college.mobile = mobile
        if address:
            college.address = address
        db.session.commit()
        return college, None

    @staticmethod
    def get_qr_info(user_id, base_frontend_url="http://localhost:5173"):
        college = College.query.filter_by(user_id=user_id).first()
        if not college:
            return None, "College not found."

        connect_url = f"{base_frontend_url}/college-connect/{college.qr_token}"
        qr_base64 = generate_qr_base64(connect_url)

        return {
            "college_id": college.college_id,
            "college_name": college.college_name,
            "qr_token": college.qr_token,
            "secure_link_token": college.secure_link_token,
            "connect_url": connect_url,
            "qr_base64": qr_base64
        }, None

    @staticmethod
    def get_dashboard_stats(user_id):
        college = College.query.filter_by(user_id=user_id).first()
        if not college:
            return {}

        linked_students = CollegeStudentLink.query.filter_by(
            college_id=college.id,
            status='ACCEPTED'
        ).count()

        pending_reqs = CollegeStudentLink.query.filter_by(
            college_id=college.id,
            status='PENDING'
        ).count()

        # Direct college documents uploaded (active, non-deleted)
        direct_docs = Document.query.filter_by(college_id=college.id, student_id=None, is_deleted=False).all()
        direct_docs_count = len(direct_docs)
        direct_doc_ids = [d.id for d in direct_docs]

        authenticated_docs = 0
        pending_docs = 0
        not_verified_docs = 0
        suspicious_docs = 0
        pending_not_verified = 0

        if direct_doc_ids:
            for d in direct_docs:
                latest_v = Verification.query.filter_by(document_id=d.id, college_id=college.id)\
                    .order_by(Verification.verification_date.desc(), Verification.id.desc()).first()
                if latest_v:
                    st = (latest_v.final_status or "").upper()
                    if st == "AUTHENTICATED":
                        authenticated_docs += 1
                    elif st in ["PENDING", "IN_PROGRESS"]:
                        pending_docs += 1
                        pending_not_verified += 1
                    elif st == "SUSPICIOUS":
                        suspicious_docs += 1
                        not_verified_docs += 1
                        pending_not_verified += 1
                    else:
                        not_verified_docs += 1
                        pending_not_verified += 1
                else:
                    pending_docs += 1
                    pending_not_verified += 1

        if direct_doc_ids:
            total_direct_verifications = Verification.query.filter(
                Verification.college_id == college.id,
                Verification.verification_source == "COLLEGE",
                Verification.document_id.in_(direct_doc_ids)
            ).count()
            recent_verifications = Verification.query.filter(
                Verification.college_id == college.id,
                Verification.verification_source == "COLLEGE",
                Verification.document_id.in_(direct_doc_ids)
            ).order_by(Verification.verification_date.desc()).limit(5).all()
        else:
            total_direct_verifications = 0
            recent_verifications = []

        return {
            "college": college.to_dict(),
            "stats": {
                "linked_students": linked_students,
                "total_students": linked_students,
                "pending_requests": pending_reqs,
                "total_documents": direct_docs_count,
                "total_direct_verifications": total_direct_verifications,
                "total_verifications": total_direct_verifications,
                "verified_documents": authenticated_docs,
                "authenticated_documents": authenticated_docs,
                "pending_documents": pending_docs,
                "pending_not_verified": pending_not_verified,
                "not_verified_documents": not_verified_docs,
                "suspicious_documents": suspicious_docs,
                "recent_verifications": len(recent_verifications)
            },
            "recent_verifications": [v.to_dict() for v in recent_verifications]
        }
