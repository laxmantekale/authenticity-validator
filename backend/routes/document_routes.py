import os
import uuid
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from models.blockchain_record import BlockchainRecord
from models.college_student_link import CollegeStudentLink
from config import Config

document_bp = Blueprint("document", __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_document():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    student_id_val = None
    college_id_val = None

    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        student_id_val = student.id
        college_id_arg = request.form.get("college_id")
        if college_id_arg and str(college_id_arg).isdigit():
            college_id_val = int(college_id_arg)
    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return jsonify({"error": "College profile not found"}), 404
        college_id_val = college.id
        student_id_val = None
    else:
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format. Please upload PDF, PNG, JPG, or WEBP."}), 400

    document_type = request.form.get("document_type", "Academic Document").strip()
    custom_title = request.form.get("document_title", "").strip()

    # Read file content to generate SHA-256 hash and save
    file_bytes = file.read()
    file_size = len(file_bytes)
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()

    orig_name = secure_filename(file.filename) or f"{document_type.replace(' ', '_')}.pdf"
    ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'pdf'
    stored_name = f"{uuid.uuid4().hex}.{ext}"

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(Config.UPLOAD_FOLDER, stored_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Save document record
    doc = Document(
        student_id=student_id_val,
        college_id=college_id_val,
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

    return jsonify({
        "success": True,
        "message": "Document uploaded successfully",
        "document": doc.to_dict()
    }), 201

@document_bp.route("", methods=["GET"])
@document_bp.route("/my-documents", methods=["GET"])
@jwt_required()
def get_my_documents():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        docs = Document.query.filter_by(student_id=student.id, is_deleted=False).order_by(Document.uploaded_at.desc()).all()
        return jsonify({
            "success": True,
            "documents": [d.to_dict() for d in docs]
        }), 200

    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return jsonify({"error": "College profile not found"}), 404
        
        source = request.args.get("source", "").lower()
        
        # Accepted linked students
        links = CollegeStudentLink.query.filter(
            (CollegeStudentLink.college_id == college.id) &
            (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
        ).all()
        student_ids = [l.student_id for l in links]

        if source == "direct":
            docs = Document.query.filter(
                Document.college_id == college.id,
                Document.student_id.is_(None),
                Document.is_deleted == False
            ).order_by(Document.uploaded_at.desc()).all()
        elif source == "linked":
            docs = Document.query.filter(
                Document.student_id.in_(student_ids),
                Document.is_deleted == False
            ).order_by(Document.uploaded_at.desc()).all() if student_ids else []
        else:
            docs = Document.query.filter(
                (Document.college_id == college.id) | (Document.student_id.in_(student_ids) if student_ids else False),
                Document.is_deleted == False
            ).order_by(Document.uploaded_at.desc()).all()
        
        return jsonify({
            "success": True,
            "documents": [d.to_dict() for d in docs]
        }), 200

    return jsonify({"error": "Unauthorized"}), 403

@document_bp.route("/<int:doc_id>", methods=["GET"])
@jwt_required()
def get_document_details(doc_id):
    doc = db.session.get(Document, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        if not student or doc.student_id != student.id:
            return jsonify({"error": "Access denied"}), 403
    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return jsonify({"error": "College not found"}), 404
        if doc.college_id != college.id:
            link = CollegeStudentLink.query.filter_by(college_id=college.id, student_id=doc.student_id, status="ACCEPTED").first()
            if not link:
                return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "success": True,
        "document": doc.to_dict()
    }), 200

@document_bp.route("/<int:doc_id>/view", methods=["GET"])
@document_bp.route("/<int:doc_id>/file", methods=["GET"])
def view_document_file(doc_id):
    doc = db.session.get(Document, doc_id)
    if not doc or not os.path.exists(doc.file_path):
        return jsonify({"error": "Document file not found"}), 404

    return send_file(
        doc.file_path,
        mimetype=doc.mime_type or "application/pdf",
        as_attachment=False
    )

@document_bp.route("/<int:doc_id>", methods=["DELETE"])
@jwt_required()
def delete_document(doc_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    doc = db.session.get(Document, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    # Strict authorization checks
    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        if not student or doc.student_id != student.id:
            return jsonify({"error": "Access denied. You can only delete your own documents."}), 403
    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college or doc.college_id != college.id:
            return jsonify({"error": "Access denied. College not authorized for this document."}), 403
        if doc.student_id is not None:
            return jsonify({"error": "Institutions can only delete direct college uploads, not student-uploaded documents."}), 403
    else:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # 1. Identify all associated verification IDs
        verifications = Verification.query.filter_by(document_id=doc.id).all()
        ver_ids = [v.id for v in verifications]

        # 2. Collect all physical file paths for safe disk deletion
        files_to_delete = []
        if doc.file_path:
            files_to_delete.append(doc.file_path)
        if doc.stored_filename:
            stored_path = os.path.join(Config.UPLOAD_FOLDER, doc.stored_filename)
            files_to_delete.append(stored_path)

        reports = []
        if ver_ids:
            reports = Report.query.filter(Report.verification_id.in_(ver_ids)).all()
            for rep in reports:
                if rep.report_file_path:
                    files_to_delete.append(rep.report_file_path)
                if rep.report_id:
                    rep_path = os.path.join(Config.REPORT_FOLDER, f"{rep.report_id}.pdf")
                    files_to_delete.append(rep_path)

        # 3. Preserve immutable external blockchain records by dissociating document and verification foreign keys
        try:
            if ver_ids:
                BlockchainRecord.query.filter(
                    (BlockchainRecord.document_id == doc.id) |
                    (BlockchainRecord.verification_id.in_(ver_ids))
                ).update({"document_id": None, "verification_id": None}, synchronize_session=False)
            else:
                BlockchainRecord.query.filter_by(document_id=doc.id).update(
                    {"document_id": None, "verification_id": None}, synchronize_session=False
                )
        except Exception as bc_err:
            print(f"Blockchain dissociation notice: {bc_err}")

        # 4. Cascade delete VerificationHistory records associated with this document
        if ver_ids:
            VerificationHistory.query.filter(
                (VerificationHistory.document_id == doc.id) |
                (VerificationHistory.verification_id.in_(ver_ids))
            ).delete(synchronize_session=False)
        else:
            VerificationHistory.query.filter_by(document_id=doc.id).delete(synchronize_session=False)

        # 5. Delete Report records
        for rep in reports:
            db.session.delete(rep)

        # 6. Delete Verification records
        for ver in verifications:
            db.session.delete(ver)

        # 7. Permanently delete Document record
        db.session.delete(doc)

        # 8. Commit database transaction atomically
        db.session.commit()

        # 9. Safely remove physical files from storage after database commit
        file_warnings = []
        for file_path in set(files_to_delete):
            if not file_path:
                continue
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as f_err:
                print(f"Physical file removal warning for {file_path}: {f_err}")
                file_warnings.append(f"{os.path.basename(file_path)}: {str(f_err)}")

        partial_cleanup = len(file_warnings) > 0
        return jsonify({
            "success": True,
            "partial_file_cleanup": partial_cleanup,
            "message": (
                "Document and all associated verification history, reports, and files permanently deleted."
                if not partial_cleanup else
                "Document and database records permanently deleted. Note: some physical files could not be unlinked."
            ),
            "file_warnings": file_warnings if partial_cleanup else None
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500
