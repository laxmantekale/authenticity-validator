import os
import json
import io
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from models.report import Report
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.college_student_link import CollegeStudentLink
from services.report_service import ReportService
from config import Config

report_bp = Blueprint("report", __name__)

def check_report_access(report, user_id, role):
    """Verifies that the authenticated user owns or has official rights to the report."""
    if not report:
        return False
    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        return bool(student and report.student_id == student.id)
    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return False
        if report.college_id == college.id:
            return True
        if report.student_id:
            link = CollegeStudentLink.query.filter_by(
                college_id=college.id,
                student_id=report.student_id,
                status="ACCEPTED"
            ).first()
            return bool(link)
    return False

def ensure_report_pdf(report):
    """Ensures PDF file exists on disk, regenerating with complete verification data if absent."""
    if not report.report_file_path or not os.path.exists(report.report_file_path):
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
        student_name = report.student.full_name if report.student else "Candidate"
        student_id_code = report.student.student_id if report.student else "STUDENT"
        doc_hash = report.verification.document.file_hash if (report.verification and report.verification.document) else ""
        doc_type = report.verification.document.document_type if (report.verification and report.verification.document) else "Academic Document"
        
        parsed_data = report.get_parsed_report_data()

        pdf_path = ReportService.generate_pdf_report(
            student_name=student_name,
            student_id=student_id_code,
            document_name=report.document_name,
            auth_status=report.authentication_status,
            report_id=report.report_id,
            verification_date=report.generated_at,
            doc_hash=doc_hash,
            doc_type=doc_type,
            checks=parsed_data.get("checks", {}),
            full_verification_data=parsed_data
        )
        report.report_file_path = pdf_path
        db.session.commit()
    return report.report_file_path

@report_bp.route("", methods=["GET"])
@report_bp.route("/my-reports", methods=["GET"])
@jwt_required()
def get_my_reports():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "student":
        student = Student.query.filter_by(user_id=int(user_id)).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        reports = Report.query.join(Verification, Report.verification_id == Verification.id)\
            .join(Document, Verification.document_id == Document.id)\
            .filter(Report.student_id == student.id, Document.is_deleted == False)\
            .order_by(Report.generated_at.desc()).all()
        return jsonify({
            "success": True,
            "reports": [r.to_dict() for r in reports]
        }), 200

    elif role == "college":
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return jsonify({"error": "College not found"}), 404
        links = CollegeStudentLink.query.filter(
            (CollegeStudentLink.college_id == college.id) &
            (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
        ).all()
        student_ids = [l.student_id for l in links]
        reports = Report.query.join(Verification, Report.verification_id == Verification.id)\
            .join(Document, Verification.document_id == Document.id)\
            .filter(
                Document.is_deleted == False,
                (Report.college_id == college.id) | (Report.student_id.in_(student_ids) if student_ids else False)
            ).order_by(Report.generated_at.desc()).all()
        return jsonify({
            "success": True,
            "reports": [r.to_dict() for r in reports]
        }), 200

    return jsonify({"error": "Unauthorized"}), 403

@report_bp.route("/<report_id_code>/details", methods=["GET"])
@jwt_required()
def get_report_details(report_id_code):
    """
    Returns complete 9-section structured verification report for web viewer rendering.
    Enforces ownership and access verification.
    """
    report = Report.query.filter_by(report_id=report_id_code).first()
    if not report:
        return jsonify({"error": "Report record not found"}), 404

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if not check_report_access(report, user_id, role):
        return jsonify({"error": "Access denied. You do not have permission to view this report."}), 403

    return jsonify({
        "success": True,
        "report": report.to_full_details()
    }), 200

@report_bp.route("/<report_id_code>/json", methods=["GET"])
@jwt_required()
def download_report_json(report_id_code):
    """
    Downloads the complete structured verification report as a JSON file.
    """
    report = Report.query.filter_by(report_id=report_id_code).first()
    if not report:
        return jsonify({"error": "Report record not found"}), 404

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if not check_report_access(report, user_id, role):
        return jsonify({"error": "Access denied. You do not have permission to download this report."}), 403

    details = report.to_full_details()
    json_bytes = json.dumps(details, indent=2).encode('utf-8')
    mem_file = io.BytesIO(json_bytes)
    mem_file.seek(0)

    return send_file(
        mem_file,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"Verification_Report_{report_id_code}.json"
    )

@report_bp.route("/download/<report_id_code>", methods=["GET"])
@report_bp.route("/<report_id_code>/download", methods=["GET"])
@jwt_required(optional=True)
def download_report(report_id_code):
    report = Report.query.filter_by(report_id=report_id_code).first()
    if not report:
        return jsonify({"error": "Report record not found"}), 404

    user_id = get_jwt_identity()
    if user_id:
        claims = get_jwt()
        role = claims.get("role")
        if not check_report_access(report, user_id, role):
            return jsonify({"error": "Access denied. You do not have permission to download this report."}), 403

    pdf_path = ensure_report_pdf(report)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "Report file generation failed"}), 500

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Verification_Report_{report_id_code}.pdf"
    )

@report_bp.route("/view/<report_id_code>", methods=["GET"])
@report_bp.route("/<report_id_code>/view", methods=["GET"])
@jwt_required(optional=True)
def view_report(report_id_code):
    report = Report.query.filter_by(report_id=report_id_code).first()
    if not report:
        return jsonify({"error": "Report record not found"}), 404

    user_id = get_jwt_identity()
    if user_id:
        claims = get_jwt()
        role = claims.get("role")
        if not check_report_access(report, user_id, role):
            return jsonify({"error": "Access denied. You do not have permission to view this report."}), 403

    pdf_path = ensure_report_pdf(report)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "Report file generation failed"}), 500

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=False
    )

@report_bp.route("/download-complete", methods=["GET"])
@report_bp.route("/student/<int:student_id>/download-complete", methods=["GET"])
@jwt_required()
def download_complete_report(student_id=None):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    target_student = None
    if role == "student":
        target_student = Student.query.filter_by(user_id=int(user_id)).first()
    elif role == "college" and student_id:
        college = College.query.filter_by(user_id=int(user_id)).first()
        if not college:
            return jsonify({"error": "College not found"}), 404
        link = CollegeStudentLink.query.filter_by(college_id=college.id, student_id=student_id, status="ACCEPTED").first()
        if not link:
            return jsonify({"error": "Access denied. Student is not enrolled with this institution."}), 403
        target_student = Student.query.get(student_id)

    if not target_student:
        return jsonify({"error": "Student record not found"}), 404

    reports = Report.query.filter_by(student_id=target_student.id).order_by(Report.generated_at.desc()).all()
    if not reports:
        return jsonify({"error": "No authenticated documents available for report generation."}), 404

    verified_items = []
    for r in reports:
        doc_type = r.verification.document.document_type if (r.verification and r.verification.document) else r.document_name
        verified_items.append({
            "title": doc_type or r.document_name,
            "status": "Authenticated" if "AUTH" in r.authentication_status.upper() and "NOT" not in r.authentication_status.upper() else "Not Authenticated",
            "date": r.generated_at.strftime("%d/%m/%Y") if r.generated_at else "N/A",
            "ver_id": r.report_id
        })

    comp_report_id = f"COMP-AVR-{target_student.student_id}-{int(os.urandom(2).hex(), 16)}"
    pdf_path = ReportService.generate_complete_student_report(
        student_name=target_student.full_name,
        student_id=target_student.student_id,
        verified_items=verified_items,
        report_id=comp_report_id
    )

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Complete_Authentication_Report_{target_student.student_id}.pdf"
    )

@report_bp.route("/college/download-audit", methods=["GET"])
@jwt_required()
def download_college_audit():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role != "college":
        return jsonify({"error": "Unauthorized"}), 403

    college = College.query.filter_by(user_id=int(user_id)).first()
    if not college:
        return jsonify({"error": "College not found"}), 404

    links = CollegeStudentLink.query.filter(
        (CollegeStudentLink.college_id == college.id) &
        (CollegeStudentLink.status.in_(["ACCEPTED", "accepted"]))
    ).all()
    student_ids = [l.student_id for l in links]

    history = VerificationHistory.query.filter(
        (VerificationHistory.college_id == college.id) |
        (VerificationHistory.student_id.in_(student_ids) if student_ids else False)
    ).order_by(VerificationHistory.verification_date.desc()).all()

    if not history:
        return jsonify({"error": "No audit records available for export."}), 404

    audit_items = []
    for h in history:
        doc_type = h.document.document_type if h.document else h.document_name
        student_name = h.student.full_name if h.student else "Candidate"
        student_code = h.student.student_id if h.student else f"STU{h.student_id}"
        audit_items.append({
            "student_name": student_name,
            "student_id_code": student_code,
            "document_name": doc_type or h.document_name,
            "status": "Authenticated" if "AUTH" in h.authentication_status.upper() and "NOT" not in h.authentication_status.upper() else "Not Authenticated",
            "date": h.verification_date.strftime("%d/%m/%Y") if h.verification_date else "N/A",
            "report_id": h.report_id or "N/A"
        })

    audit_report_id = f"AUDIT-COL-{college.college_id}-{int(os.urandom(2).hex(), 16)}"
    pdf_path = ReportService.generate_college_audit_report(
        college_name=college.college_name,
        college_code=college.college_id,
        audit_items=audit_items,
        report_id=audit_report_id
    )

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Institutional_Audit_Report_{college.college_id}.pdf"
    )
