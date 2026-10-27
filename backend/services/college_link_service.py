from datetime import datetime
from extensions import db
from models.college import College
from models.student import Student
from models.college_student_link import CollegeStudentLink

class CollegeLinkService:
    @staticmethod
    def request_link(student_user_id, college_identifier):
        student = Student.query.filter_by(user_id=student_user_id).first()
        if not student:
            return None, "Student profile not found."

        college = College.query.filter(
            (College.college_id == college_identifier) |
            (College.qr_token == college_identifier) |
            (College.secure_link_token == college_identifier)
        ).first()

        if not college:
            return None, f"No college found for identifier: {college_identifier}"

        existing = CollegeStudentLink.query.filter_by(
            student_id=student.id,
            college_id=college.id
        ).first()

        if existing:
            if existing.status == 'ACCEPTED':
                return existing, "Already connected to this institution."
            elif existing.status == 'PENDING':
                return existing, "A link request is already pending approval."
            else:
                existing.status = 'PENDING'
                existing.requested_at = datetime.utcnow()
                existing.accepted_at = None
                existing.rejected_at = None
                existing.unlinked_at = None
                existing.unlinked_by = None
                db.session.commit()
                return existing, None

        new_link = CollegeStudentLink(
            student_id=student.id,
            college_id=college.id,
            status='PENDING',
            requested_at=datetime.utcnow()
        )
        db.session.add(new_link)
        db.session.commit()
        return new_link, None

    @staticmethod
    def respond_request(college_user_id, link_id, action):
        college = College.query.filter_by(user_id=college_user_id).first()
        if not college:
            return None, "College not found."

        link = CollegeStudentLink.query.filter_by(id=link_id, college_id=college.id).first()
        if not link:
            return None, "Link request not found."

        if action.lower() in ['accept', 'accepted']:
            link.status = 'ACCEPTED'
            link.accepted_at = datetime.utcnow()
            link.rejected_at = None
        elif action.lower() in ['reject', 'rejected']:
            link.status = 'REJECTED'
            link.rejected_at = datetime.utcnow()
            link.accepted_at = None
        else:
            return None, "Invalid response action."

        db.session.commit()
        return link, None

    @staticmethod
    def unlink_by_student(student_user_id, college_id):
        student = Student.query.filter_by(user_id=student_user_id).first()
        if not student:
            return None, "Student profile not found."

        # Support both college table id and college_id string
        link = CollegeStudentLink.query.filter(
            (CollegeStudentLink.student_id == student.id) &
            (CollegeStudentLink.college_id == college_id) &
            (CollegeStudentLink.status == 'ACCEPTED')
        ).first()

        if not link:
            # Check if college_id passed was the College entity ID vs link ID
            link = CollegeStudentLink.query.filter_by(id=college_id, student_id=student.id, status='ACCEPTED').first()

        if not link:
            return None, "Active college connection not found."

        link.status = 'UNLINKED'
        link.unlinked_at = datetime.utcnow()
        link.unlinked_by = 'STUDENT'
        db.session.commit()
        return link, None

    @staticmethod
    def remove_by_college(college_user_id, student_id):
        college = College.query.filter_by(user_id=college_user_id).first()
        if not college:
            return None, "College profile not found."

        link = CollegeStudentLink.query.filter(
            (CollegeStudentLink.college_id == college.id) &
            (CollegeStudentLink.student_id == student_id) &
            (CollegeStudentLink.status == 'ACCEPTED')
        ).first()

        if not link:
            link = CollegeStudentLink.query.filter_by(id=student_id, college_id=college.id, status='ACCEPTED').first()

        if not link:
            return None, "Active linked student not found."

        link.status = 'REMOVED'
        link.unlinked_at = datetime.utcnow()
        link.unlinked_by = 'COLLEGE'
        db.session.commit()
        return link, None
