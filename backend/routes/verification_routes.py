import os
import uuid
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from services.verification_service import verification_service
from config import Config

verification_bp = Blueprint("verification", __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@verification_bp.route("/verify/<int:doc_id>", methods=["POST"])
@jwt_required()
def verify_document_endpoint(doc_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    result, err = verification_service.verify_document(
        document_id=doc_id,
        user_id=user_id,
        role=role
    )
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200

@verification_bp.route("/student", methods=["POST"])
@jwt_required()
def verify_student_direct():
    """
    Direct student verification endpoint:
    Uploads file and verifies it immediately for the student.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "student":
        return jsonify({"error": "Only students can use student verification endpoint"}), 403

    student = Student.query.filter_by(user_id=int(user_id)).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    # If document_id is passed as json
    if request.is_json:
        data = request.get_json() or {}
        doc_id = data.get("document_id")
        if not doc_id:
            return jsonify({"error": "document_id is required"}), 400
        result, err = verification_service.verify_document(
            document_id=doc_id,
            user_id=user_id,
            role="student"
        )
        if err:
            return jsonify({"error": err}), 400
        return jsonify(result), 200

    try:
        file = request.files.get('file') or request.files.get('document')
        if not file or file.filename == '':
            return jsonify({"error": "No file uploaded"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file format. Please upload PDF, PNG, JPG, or WEBP."}), 400

        document_type = request.form.get("document_type", "Academic Document").strip()
        custom_title = request.form.get("document_title", "").strip()

        file_bytes = file.read()
        file_size = len(file_bytes)
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        orig_name = secure_filename(file.filename) or f"{document_type.replace(' ', '_')}.pdf"
        ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'pdf'
        stored_name = f"stu_{uuid.uuid4().hex}.{ext}"

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.UPLOAD_FOLDER, stored_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        doc = Document(
            student_id=student.id,
            college_id=None,
            document_type=document_type,
            original_filename=custom_title or orig_name,
            stored_filename=stored_name,
            file_path=file_path,
            file_size=file_size,
            file_hash=sha256_hash,
            mime_type=file.mimetype or "application/pdf"
        )
        db.session.add(doc)
        db.session.commit()

        result, err = verification_service.verify_document(
            document_id=doc.id,
            user_id=user_id,
            role="student"
        )
        if err:
            return jsonify({"error": err}), 400

        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Document processing failed: {str(e)}"}), 500

@verification_bp.route("/college", methods=["POST"])
@jwt_required()
def verify_college_direct():
    """
    Direct college verification endpoint:
    Uploads file and verifies it immediately for the college without requiring any student linking.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "college":
        return jsonify({"error": "Only colleges can perform direct college verification"}), 403

    college = College.query.filter_by(user_id=int(user_id)).first()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    try:
        file = request.files.get('file') or request.files.get('document')
        if not file or file.filename == '':
            return jsonify({"error": "No file uploaded"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file format. Please upload PDF, PNG, JPG, or WEBP."}), 400

        document_type = request.form.get("document_type", "Academic Document").strip()
        candidate_name = request.form.get("candidate_name", "Walk-in Candidate").strip()
        custom_title = request.form.get("document_title", "").strip()

        file_bytes = file.read()
        file_size = len(file_bytes)
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        orig_name = secure_filename(file.filename) or f"{document_type.replace(' ', '_')}.pdf"
        ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'pdf'
        stored_name = f"col_{uuid.uuid4().hex}.{ext}"

        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.UPLOAD_FOLDER, stored_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Create Document record with student_id=None, college_id=college.id
        doc = Document(
            student_id=None,
            college_id=college.id,
            document_type=document_type,
            original_filename=custom_title or orig_name,
            stored_filename=stored_name,
            file_path=file_path,
            file_size=file_size,
            file_hash=sha256_hash,
            mime_type=file.mimetype or "application/pdf"
        )
        db.session.add(doc)
        db.session.commit()

        # Run verification pipeline
        result, err = verification_service.verify_document(
            document_id=doc.id,
            user_id=user_id,
            role="college",
            candidate_name=candidate_name
        )
        if err:
            return jsonify({"error": err}), 400

        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Document processing failed: {str(e)}"}), 500

@verification_bp.route("/status/<int:verification_id>", methods=["GET"])
@jwt_required()
def get_verification_status(verification_id):
    v = db.session.get(Verification, verification_id)
    if not v:
        return jsonify({"error": "Verification record not found"}), 404

    return jsonify({"verification": v.to_dict()}), 200

@verification_bp.route("/history", methods=["GET"])
@jwt_required()
def get_student_verification_history():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "student":
        return jsonify({"error": "Unauthorized"}), 403

    student = Student.query.filter_by(user_id=int(user_id)).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    # Strict separation: Return only records verified by the student
    history = VerificationHistory.query.filter_by(
        student_id=student.id,
        verification_source="STUDENT"
    ).order_by(VerificationHistory.verification_date.desc()).all()

    return jsonify({"history": [h.to_dict() for h in history]}), 200

@verification_bp.route("/college-history", methods=["GET"])
@jwt_required()
def get_college_verification_history():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "college":
        return jsonify({"error": "Unauthorized"}), 403

    college = College.query.filter_by(user_id=int(user_id)).first()
    if not college:
        return jsonify({"error": "College profile not found"}), 404

    # Strict separation: Return only records directly verified by this college
    history = VerificationHistory.query.filter_by(
        college_id=college.id,
        verification_source="COLLEGE"
    ).order_by(VerificationHistory.verification_date.desc()).all()

    return jsonify({"history": [h.to_dict() for h in history]}), 200
