import io
import os
import uuid
import hashlib
import base64
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import qrcode
from extensions import db
from models.user import User
from models.college import College
from models.student import Student
from models.college_student_link import CollegeStudentLink
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from models.blockchain_record import BlockchainRecord
from services.verification_service import verification_service
from services.report_service import ReportService
from config import Config

college_bp = Blueprint("college", __name__)

def get_current_college():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") != "college":
        return None
    return College.query.filter_by(user_id=int(user_id)).first()

@college_bp.route("/dashboard-stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    # Linked students count
    accepted_links = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).all()
    linked_students_count = len(accepted_links)
    student_ids = [l.student_id for l in accepted_links]

    # Pending link requests
    pending_requests_count = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (CollegeStudentLink.status.in_(["PENDING", "pending"]))
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

    # Total direct verifications and history for existing direct documents
    if direct_doc_ids:
        total_direct_verifications = Verification.query.filter(
            Verification.college_id == college.id,
            Verification.verification_source == "COLLEGE",
            Verification.document_id.in_(direct_doc_ids)
        ).count()
        total_history = VerificationHistory.query.filter(
            VerificationHistory.college_id == college.id,
            VerificationHistory.verification_source == "COLLEGE",
            VerificationHistory.document_id.in_(direct_doc_ids)
        ).count()
        recent_activity = [
            v.to_dict() for v in Verification.query.filter(
                Verification.college_id == college.id,
                Verification.verification_source == "COLLEGE",
                Verification.document_id.in_(direct_doc_ids)
            ).order_by(Verification.verification_date.desc(), Verification.id.desc()).limit(5).all()
        ]
    else:
        total_direct_verifications = 0
        total_history = 0
        recent_activity = []

    recent_requests = [
        l.to_dict() for l in CollegeStudentLink.query.filter(
            (CollegeStudentLink.college_id == college.id) &
            (CollegeStudentLink.status.in_(["PENDING", "pending"]))
        ).order_by(CollegeStudentLink.requested_at.desc()).limit(5).all()
    ]

    return jsonify({
        "stats": {
            "total_documents": direct_docs_count,
            "total_direct_verifications": total_direct_verifications,
            "total_verifications": total_direct_verifications,
            "verified_documents": authenticated_docs,
            "authenticated_documents": authenticated_docs,
            "authenticated": authenticated_docs,
            "pending_documents": pending_docs,
            "pending_verifications": pending_docs,
            "pending": pending_docs,
            "pending_not_verified": pending_not_verified,
            "not_verified_documents": not_verified_docs,
            "not_verified": not_verified_docs,
            "suspicious_documents": suspicious_docs,
            "total_history": total_history,
            "verification_history": total_history,
            "linked_students": linked_students_count,
            "total_students": linked_students_count,
            "pending_requests": pending_requests_count,
            "pending_student_requests": pending_requests_count
        },
        "college": college.to_dict(),
        "recent_requests": recent_requests,
        "recent_activity": recent_activity
    }), 200

@college_bp.route("/profile", methods=["GET", "PUT"])
@jwt_required()
def profile():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    if request.method == "GET":
        return jsonify({"profile": college.to_dict()}), 200

    data = request.get_json(silent=True) or {}
    if "college_name" in data and data["college_name"].strip():
        college.college_name = data["college_name"].strip()
    if "mobile" in data and data["mobile"].strip():
        college.mobile = data["mobile"].strip()
    elif "contact_number" in data and data["contact_number"].strip():
        college.mobile = data["contact_number"].strip()
    if "address" in data and data["address"].strip():
        college.address = data["address"].strip()

    db.session.commit()
    return jsonify({"message": "College profile updated successfully", "profile": college.to_dict()}), 200

@college_bp.route("/qr", methods=["GET"])
@jwt_required()
def get_college_qr():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    qr_url = f"{Config.FRONTEND_URL}/college-connect/{college.secure_link_token}"
    
    qr_img = qrcode.make(qr_url)
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{img_str}"

    return jsonify({
        "college_name": college.college_name,
        "college_id": college.college_id,
        "college_code": college.college_id,
        "qr_token": college.qr_token,
        "secure_link_token": college.secure_link_token,
        "secure_link_slug": college.secure_link_token,
        "connect_url": qr_url,
        "qr_data_url": data_url
    }), 200

@college_bp.route("/qr/regenerate", methods=["POST"])
@jwt_required()
def regenerate_qr():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    college.qr_token = College.generate_token()
    college.secure_link_token = College.generate_token()[:12]
    db.session.commit()

    return jsonify({
        "message": "College QR and secure link regenerated successfully",
        "qr_token": college.qr_token,
        "secure_link_token": college.secure_link_token
    }), 200

@college_bp.route("/link-token", methods=["GET"])
@jwt_required()
def get_link_token():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    connect_url = f"{Config.FRONTEND_URL}/college-connect/{college.secure_link_token}"
    return jsonify({
        "college_name": college.college_name,
        "college_id": college.college_id,
        "college_code": college.college_id,
        "secure_link_token": college.secure_link_token,
        "secure_link_slug": college.secure_link_token,
        "connect_url": connect_url
    }), 200

@college_bp.route("/public-info/<identifier>", methods=["GET"])
def get_public_info(identifier):
    college = College.query.filter(
        (College.secure_link_token == identifier) |
        (College.qr_token == identifier) |
        (College.college_id == identifier.upper())
    ).first()

    if not college:
        return jsonify({"error": "College not found or invalid identifier"}), 404

    return jsonify({
        "college": college.to_dict()
    }), 200

@college_bp.route("/link-requests", methods=["GET"])
@college_bp.route("/student-requests", methods=["GET"])
@college_bp.route("/requests", methods=["GET"])
@jwt_required()
def get_link_requests():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    status_filter = request.args.get("status")
    query = CollegeStudentLink.query.filter_by(college_id=college.id)
    if status_filter and status_filter.lower() != "all":
        query = query.filter(CollegeStudentLink.status.ilike(status_filter))

    requests_list = query.order_by(CollegeStudentLink.requested_at.desc()).all()
    return jsonify({"requests": [r.to_dict() for r in requests_list]}), 200

@college_bp.route("/link-requests/<int:link_id>/respond", methods=["POST"])
@college_bp.route("/student-requests/<int:link_id>/action", methods=["POST", "PUT"])
@college_bp.route("/requests/<int:link_id>/respond", methods=["POST"])
@jwt_required()
def respond_link_request(link_id):
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    data = request.get_json(silent=True) or {}
    action = data.get("action", "").lower()  # 'accept' or 'reject'

    if action not in ["accept", "reject", "accepted", "rejected"]:
        return jsonify({"error": "Action must be 'accept' or 'reject'"}), 400

    link = CollegeStudentLink.query.filter_by(id=link_id, college_id=college.id).first()
    if not link:
        return jsonify({"error": "Link request not found"}), 404

    if action in ["accept", "accepted"]:
        link.status = "ACCEPTED"
        link.accepted_at = datetime.utcnow()
        link.rejected_at = None
        link.unlinked_at = None
        link.unlinked_by = None
    else:
        link.status = "REJECTED"
        link.rejected_at = datetime.utcnow()
        link.accepted_at = None
        link.unlinked_at = None
        link.unlinked_by = None

    db.session.commit()

    return jsonify({
        "message": f"Link request has been {link.status}",
        "link": link.to_dict()
    }), 200

@college_bp.route("/student-requests/<int:link_id>/accept", methods=["PUT", "POST"])
@jwt_required()
def accept_student_request(link_id):
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    link = CollegeStudentLink.query.filter_by(id=link_id, college_id=college.id).first()
    if not link:
        return jsonify({"error": "Link request not found"}), 404

    link.status = "ACCEPTED"
    link.accepted_at = datetime.utcnow()
    link.rejected_at = None
    link.unlinked_at = None
    link.unlinked_by = None
    db.session.commit()

    return jsonify({
        "message": "Student link request accepted successfully",
        "link": link.to_dict()
    }), 200

@college_bp.route("/student-requests/<int:link_id>/reject", methods=["PUT", "POST"])
@jwt_required()
def reject_student_request(link_id):
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    link = CollegeStudentLink.query.filter_by(id=link_id, college_id=college.id).first()
    if not link:
        return jsonify({"error": "Link request not found"}), 404

    link.status = "REJECTED"
    link.rejected_at = datetime.utcnow()
    link.accepted_at = None
    link.unlinked_at = None
    link.unlinked_by = None
    db.session.commit()

    return jsonify({
        "message": "Student link request rejected",
        "link": link.to_dict()
    }), 200

@college_bp.route("/students", methods=["GET"])
@jwt_required()
def get_linked_students():
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    links = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).all()
    student_ids = [l.student_id for l in links]
    
    students = Student.query.filter(Student.id.in_(student_ids)).all() if student_ids else []
    
    # Map link info
    link_map = {l.student_id: l for l in links}
    result = []
    for s in students:
        s_dict = s.to_dict()
        docs = Document.query.filter_by(student_id=s.id).all()
        s_dict["total_documents"] = len(docs)
        s_dict["documents"] = [d.to_dict() for d in docs]
        link_obj = link_map.get(s.id)
        if link_obj:
            s_dict["linked_at"] = link_obj.accepted_at.isoformat() if link_obj.accepted_at else link_obj.created_at.isoformat()
            s_dict["link_id"] = link_obj.id
        result.append(s_dict)

    return jsonify({"students": result}), 200

@college_bp.route("/students/<int:student_id>/remove", methods=["POST", "DELETE"])
@college_bp.route("/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def remove_linked_student(student_id):
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    try:
        sid_int = int(student_id)
    except Exception:
        sid_int = None

    matched_student_ids = []
    if sid_int:
        matched_student_ids.append(sid_int)
        stu_by_user = Student.query.filter_by(user_id=sid_int).first()
        if stu_by_user:
            matched_student_ids.append(stu_by_user.id)

    # Locate link
    link = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (
            (CollegeStudentLink.student_id.in_(matched_student_ids)) |
            (CollegeStudentLink.id == sid_int)
        ) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).first()

    if not link:
        return jsonify({"error": "Active linked student connection not found"}), 404

    # Update status to REMOVED (never delete data)
    link.status = "REMOVED"
    link.unlinked_at = datetime.utcnow()
    link.unlinked_by = "COLLEGE"
    db.session.commit()

    return jsonify({
        "message": "Student removed from institution successfully. Historical records preserved.",
        "link": link.to_dict()
    }), 200

@college_bp.route("/student/<int:student_id>/documents", methods=["GET"])
@college_bp.route("/students/<int:student_id>/documents", methods=["GET"])
@jwt_required()
def get_student_documents(student_id):
    college = get_current_college()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    link = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (CollegeStudentLink.student_id == student_id) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).first()
    if not link:
        return jsonify({"error": "Access denied. Student is not linked to this college."}), 403

    docs = Document.query.filter_by(student_id=student_id, is_deleted=False).all()
    return jsonify({"documents": [d.to_dict() for d in docs]}), 200

