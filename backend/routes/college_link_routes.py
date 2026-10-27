from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.college_link_service import CollegeLinkService
from models.user import User
from models.student import Student
from models.college import College
from models.college_student_link import CollegeStudentLink

college_link_bp = Blueprint("college_links", __name__, url_prefix="/api/college-links")

@college_link_bp.route("/request", methods=["POST"])
@jwt_required()
def request_link():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    college_id_or_token = data.get("college_id") or data.get("identifier") or data.get("token")

    if not college_id_or_token:
        return jsonify({"error": "College identifier is required."}), 400

    link, err = CollegeLinkService.request_link(user_id, college_id_or_token)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Link request submitted successfully.",
        "link": link.to_dict()
    }), 201

@college_link_bp.route("/student", methods=["GET"])
@jwt_required()
def get_student_links():
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"links": []}), 200

    links = CollegeStudentLink.query.filter_by(student_id=student.id).all()
    return jsonify({"links": [l.to_dict() for l in links]}), 200

@college_link_bp.route("/college/requests", methods=["GET"])
@jwt_required()
def get_college_requests():
    user_id = int(get_jwt_identity())
    college = College.query.filter_by(user_id=user_id).first()
    if not college:
        return jsonify({"requests": []}), 200

    reqs = CollegeStudentLink.query.filter_by(college_id=college.id, status="PENDING").all()
    return jsonify({"requests": [r.to_dict() for r in reqs]}), 200

@college_link_bp.route("/<int:link_id>/accept", methods=["PUT", "POST"])
@jwt_required()
def accept_link(link_id):
    user_id = int(get_jwt_identity())
    link, err = CollegeLinkService.respond_request(user_id, link_id, "accept")
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Student link accepted successfully.", "link": link.to_dict()}), 200

@college_link_bp.route("/<int:link_id>/reject", methods=["PUT", "POST"])
@jwt_required()
def reject_link(link_id):
    user_id = int(get_jwt_identity())
    link, err = CollegeLinkService.respond_request(user_id, link_id, "reject")
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Student link rejected.", "link": link.to_dict()}), 200
