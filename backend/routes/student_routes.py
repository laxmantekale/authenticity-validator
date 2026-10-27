from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from models.college_student_link import CollegeStudentLink
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory

student_bp = Blueprint("student", __name__)

def get_current_student():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") != "student":
        return None
    return Student.query.filter_by(user_id=int(user_id)).first()

@student_bp.route("/dashboard-stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    # 1. Total Documents: Count only documents that currently exist and belong to the authenticated user
    docs = Document.query.filter_by(student_id=student.id, is_deleted=False).all()
    total_docs = len(docs)
    doc_ids = [d.id for d in docs]

    auth_docs = 0
    pending_count = 0
    not_verified_count = 0

    if doc_ids:
        for d in docs:
            # Query the latest persisted verification result for this document
            latest_v = Verification.query.filter_by(document_id=d.id)\
                .order_by(Verification.verification_date.desc(), Verification.id.desc()).first()
            if latest_v:
                st = (latest_v.final_status or "").upper()
                if st == "AUTHENTICATED":
                    auth_docs += 1
                elif st in ["PENDING", "IN_PROGRESS"]:
                    pending_count += 1
                else:
                    # SUSPICIOUS, NOT_VERIFIED, VERIFICATION_FAILED, NOT_AUTHENTICATED, REJECTED
                    not_verified_count += 1
            else:
                # Document uploaded but not verified yet
                pending_count += 1

    pending_or_not_verified = pending_count + not_verified_count

    # 2. Verification History: Count only history events belonging to documents that still exist
    if doc_ids:
        total_history = VerificationHistory.query.filter(
            VerificationHistory.student_id == student.id,
            VerificationHistory.document_id.in_(doc_ids)
        ).count()
        recent_verifications = [
            v.to_dict() for v in Verification.query.filter(
                Verification.student_id == student.id,
                Verification.document_id.in_(doc_ids)
            ).order_by(Verification.verification_date.desc(), Verification.id.desc()).limit(5).all()
        ]
    else:
        total_history = 0
        recent_verifications = []

    linked_colleges = CollegeStudentLink.query.filter(
        (CollegeStudentLink.student_id == student.id) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).count()
    pending_requests = CollegeStudentLink.query.filter(
        (CollegeStudentLink.student_id == student.id) &
        (CollegeStudentLink.status.in_(["PENDING", "pending"]))
    ).count()

    return jsonify({
        "stats": {
            "total_documents": total_docs,
            "total_verifications": total_history,
            "verified_documents": auth_docs,
            "authenticated": auth_docs,
            "authenticated_documents": auth_docs,
            "pending_not_verified": pending_or_not_verified,
            "pending": pending_count,
            "pending_verifications": pending_count,
            "not_verified": not_verified_count,
            "not_authenticated_documents": not_verified_count,
            "total_history": total_history,
            "verification_history": total_history,
            "linked_colleges": linked_colleges,
            "pending_requests": pending_requests
        },
        "student": student.to_dict(),
        "recent_verifications": recent_verifications
    }), 200

@student_bp.route("/profile", methods=["GET", "PUT"])
@jwt_required()
def profile():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    if request.method == "GET":
        prof = student.to_dict()
        active_link = CollegeStudentLink.query.filter(
            (CollegeStudentLink.student_id == student.id) &
            (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
        ).first()
        prof["college_name"] = active_link.college.college_name if (active_link and active_link.college) else "Not Connected"
        prof["college_id"] = active_link.college.college_id if (active_link and active_link.college) else None
        return jsonify({"profile": prof}), 200

    data = request.get_json(silent=True) or {}
    if "full_name" in data and data["full_name"].strip():
        student.full_name = data["full_name"].strip()
    if "mobile" in data and data["mobile"].strip():
        student.mobile = data["mobile"].strip()
    elif "mobile_number" in data and data["mobile_number"].strip():
        student.mobile = data["mobile_number"].strip()

    db.session.commit()
    return jsonify({"message": "Profile updated successfully", "profile": student.to_dict()}), 200

@student_bp.route("/colleges", methods=["GET"])
@jwt_required()
def get_my_colleges():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    links = CollegeStudentLink.query.filter_by(student_id=student.id).all()
    
    linked = [l.to_dict() for l in links if (l.status or "").upper() == "ACCEPTED"]
    pending = [l.to_dict() for l in links if (l.status or "").upper() == "PENDING"]
    rejected = [l.to_dict() for l in links if (l.status or "").upper() == "REJECTED"]
    unlinked = [l.to_dict() for l in links if (l.status or "").upper() in ["UNLINKED", "REMOVED"]]

    return jsonify({
        "linked_colleges": linked,
        "pending_requests": pending,
        "rejected_requests": rejected,
        "unlinked_colleges": unlinked
    }), 200

@student_bp.route("/colleges/search", methods=["GET", "POST"])
@jwt_required()
def search_colleges():
    query_str = ""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        query_str = data.get("query", "").strip()
    else:
        query_str = request.args.get("query", "").strip()

    if not query_str:
        colleges = College.query.limit(20).all()
    else:
        colleges = College.query.filter(
            (College.college_name.ilike(f"%{query_str}%")) |
            (College.college_id.ilike(f"%{query_str}%"))
        ).all()

    return jsonify({
        "colleges": [c.to_dict() for c in colleges]
    }), 200

@student_bp.route("/colleges/request-link", methods=["POST"])
@student_bp.route("/colleges/<int:college_id_path>/request", methods=["POST"])
@jwt_required()
def request_link(college_id_path=None):
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    data = request.get_json(silent=True) or {}
    college_id_param = college_id_path or data.get("college_id")
    qr_token = data.get("qr_token")
    secure_link_slug = data.get("secure_link_slug") or data.get("secure_link_token")

    target_college = None
    if college_id_param:
        try:
            target_college = db.session.get(College, int(college_id_param))
            if not target_college:
                target_college = College.query.filter_by(user_id=int(college_id_param)).first()
        except Exception:
            target_college = College.query.filter_by(college_id=str(college_id_param).upper()).first()
        if not target_college:
            target_college = College.query.filter_by(college_id=str(college_id_param).upper()).first()
    elif qr_token:
        target_college = College.query.filter_by(qr_token=qr_token).first()
    elif secure_link_slug:
        target_college = College.query.filter(
            (College.secure_link_token == secure_link_slug) |
            (College.college_id == secure_link_slug.upper())
        ).first()

    if not target_college:
        return jsonify({"error": "College not found"}), 404

    # Check if link or request already exists
    existing = CollegeStudentLink.query.filter_by(
        student_id=student.id,
        college_id=target_college.id
    ).first()

    if existing:
        status_up = (existing.status or "").upper()
        if status_up == "ACCEPTED":
            return jsonify({"error": "You are already officially linked to this college"}), 400
        elif status_up == "PENDING":
            return jsonify({"error": "A link request is already pending approval by this college"}), 400
        elif status_up in ["REJECTED", "UNLINKED", "REMOVED"]:
            existing.status = "PENDING"
            existing.requested_at = datetime.utcnow()
            existing.accepted_at = None
            existing.rejected_at = None
            existing.unlinked_at = None
            existing.unlinked_by = None
            db.session.commit()
            return jsonify({"message": f"Link request submitted to {target_college.college_name} for review", "link": existing.to_dict()}), 200

    new_link = CollegeStudentLink(
        student_id=student.id,
        college_id=target_college.id,
        status="PENDING",
        requested_at=datetime.utcnow()
    )
    db.session.add(new_link)
    db.session.commit()

    return jsonify({
        "message": f"Link request successfully sent to {target_college.college_name}. Awaiting college approval.",
        "link": new_link.to_dict()
    }), 201

@student_bp.route("/colleges/<int:college_id>/unlink", methods=["POST", "DELETE"])
@student_bp.route("/colleges/unlink", methods=["POST", "DELETE"])
@jwt_required()
def unlink_college(college_id=None):
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    if not college_id:
        data = request.get_json(silent=True) or {}
        college_id = data.get("college_id") or data.get("id")

    if not college_id:
        return jsonify({"error": "College ID is required"}), 400

    try:
        cid_int = int(college_id)
    except Exception:
        cid_int = None

    matched_college_ids = []
    if cid_int:
        matched_college_ids.append(cid_int)
        col_by_user = College.query.filter_by(user_id=cid_int).first()
        if col_by_user:
            matched_college_ids.append(col_by_user.id)

    # Locate link
    link = CollegeStudentLink.query.filter(
        (CollegeStudentLink.student_id == student.id) &
        (
            (CollegeStudentLink.college_id.in_(matched_college_ids)) |
            (CollegeStudentLink.id == cid_int)
        ) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).first()

    if not link:
        return jsonify({"error": "Active college connection not found"}), 404

    # Update status to UNLINKED (never delete data)
    link.status = "UNLINKED"
    link.unlinked_at = datetime.utcnow()
    link.unlinked_by = "STUDENT"
    db.session.commit()

    return jsonify({
        "message": "College unlinked successfully. Historical records preserved.",
        "link": link.to_dict()
    }), 200
