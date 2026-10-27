import os
import hashlib
from datetime import datetime, timedelta
from extensions import db, hash_password
from models.user import User
from models.student import Student
from models.college import College
from models.college_student_link import CollegeStudentLink
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from models.blockchain_record import BlockchainRecord
from services.report_service import ReportService
from config import Config

def seed_demo_data():
    # Only seed if no users exist
    if User.query.first():
        print("Database already contains data. Skipping demo seed.")
        return

    print("Seeding demo data for Authentication Validator...")
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORT_FOLDER, exist_ok=True)

    # 1. Create 2 Colleges
    colleges_data = [
        {
            "name": "National Institute of Technology (NIT)",
            "code": "NIT101",
            "email": "admin@nit.edu.in",
            "phone": "+91 9123456780",
            "address": "NIT Campus, Tech Park Road, Bangalore, Karnataka - 560001",
            "password": "Password@123"
        },
        {
            "name": "Metropolitan University of Technology (MUT)",
            "code": "MUT202",
            "email": "registrar@mut.edu.in",
            "phone": "+91 9123456781",
            "address": "MUT Towers, Knowledge City, New Delhi - 110001",
            "password": "Password@123"
        }
    ]

    colleges = []
    for c in colleges_data:
        user = User(
            email=c["email"],
            password_hash=hash_password(c["password"]),
            role="COLLEGE"
        )
        db.session.add(user)
        db.session.flush()

        college = College(
            user_id=user.id,
            college_id=c["code"],
            college_name=c["name"],
            official_email=c["email"],
            mobile=c["phone"],
            address=c["address"],
            qr_token=College.generate_token(),
            secure_link_token=College.generate_token()[:12]
        )
        db.session.add(college)
        colleges.append(college)

    db.session.commit()

    # 2. Create 5 Students
    students_data = [
        {"name": "Rahul Patil", "code": "STU001", "email": "rahul.patil@student.in", "mobile": "+91 9123456701", "pass": "Password@123"},
        {"name": "Amit Jadhav", "code": "STU002", "email": "amit.jadhav@student.in", "mobile": "+91 9123456702", "pass": "Password@123"},
        {"name": "Priya Sharma", "code": "STU003", "email": "priya.sharma@student.in", "mobile": "+91 9123456703", "pass": "Password@123"},
        {"name": "Sneha Kulkarni", "code": "STU004", "email": "sneha.k@student.in", "mobile": "+91 9123456704", "pass": "Password@123"},
        {"name": "Rohan Mehta", "code": "STU005", "email": "rohan.mehta@student.in", "mobile": "+91 9123456705", "pass": "Password@123"}
    ]

    students = []
    for s in students_data:
        user = User(
            email=s["email"],
            password_hash=hash_password(s["pass"]),
            role="STUDENT"
        )
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_id=s["code"],
            full_name=s["name"],
            mobile=s["mobile"]
        )
        db.session.add(student)
        students.append(student)

    db.session.commit()

    # 3. Create College Student Links
    link1 = CollegeStudentLink(student_id=students[0].id, college_id=colleges[0].id, status="ACCEPTED", requested_at=datetime.utcnow() - timedelta(days=5), accepted_at=datetime.utcnow() - timedelta(days=4))
    link2 = CollegeStudentLink(student_id=students[0].id, college_id=colleges[1].id, status="PENDING", requested_at=datetime.utcnow() - timedelta(days=1))
    link3 = CollegeStudentLink(student_id=students[1].id, college_id=colleges[0].id, status="PENDING", requested_at=datetime.utcnow() - timedelta(days=2))
    link4 = CollegeStudentLink(student_id=students[2].id, college_id=colleges[1].id, status="ACCEPTED", requested_at=datetime.utcnow() - timedelta(days=6), accepted_at=datetime.utcnow() - timedelta(days=5))
    link5 = CollegeStudentLink(student_id=students[3].id, college_id=colleges[0].id, status="REJECTED", requested_at=datetime.utcnow() - timedelta(days=10), rejected_at=datetime.utcnow() - timedelta(days=9))

    db.session.add_all([link1, link2, link3, link4, link5])
    db.session.commit()

    # 4. Create Sample Student Documents & Verifications
    sample_docs_meta = [
        {"student": students[0], "title": "Class 10th Secondary School Certificate", "type": "10th Marksheet", "filename": "10th_Marksheet_STU001.pdf", "status": "AUTHENTICATED", "college": colleges[0]},
        {"student": students[0], "title": "Class 12th Higher Secondary Marksheet", "type": "12th Marksheet", "filename": "12th_Marksheet_STU001.pdf", "status": "AUTHENTICATED", "college": colleges[0]},
        {"student": students[0], "title": "State Caste Category Certificate", "type": "Caste Certificate", "filename": "Caste_Certificate_STU001.pdf", "status": "NOT_AUTHENTICATED", "college": None},
        {"student": students[1], "title": "Bachelor of Technology Degree Certificate", "type": "Degree Certificate", "filename": "Degree_Certificate_STU002.pdf", "status": "AUTHENTICATED", "college": None},
        {"student": students[2], "title": "Annual Family Income Certificate", "type": "Income Certificate", "filename": "Income_Certificate_STU003.pdf", "status": "AUTHENTICATED", "college": colleges[1]},
        {"student": students[4], "title": "State Resident Domicile Certificate", "type": "Domicile Certificate", "filename": "Domicile_Certificate_STU005.pdf", "status": "AUTHENTICATED", "college": None}
    ]

    for idx, d_meta in enumerate(sample_docs_meta, start=1):
        stud = d_meta["student"]
        dummy_content = f"DEMO_ACADEMIC_DOCUMENT_CONTENT: {d_meta['title']} for {stud.full_name} ({stud.student_id})".encode('utf-8')
        doc_hash = hashlib.sha256(dummy_content).hexdigest()
        file_path = os.path.join(Config.UPLOAD_FOLDER, f"demo_{d_meta['filename']}")
        
        with open(file_path, "wb") as f:
            f.write(dummy_content)

        doc = Document(
            student_id=stud.id,
            college_id=d_meta["college"].id if d_meta["college"] else None,
            document_type=d_meta["type"],
            original_filename=d_meta["filename"],
            stored_filename=f"demo_{d_meta['filename']}",
            file_path=file_path,
            file_size=len(dummy_content),
            file_hash=doc_hash,
            mime_type="application/pdf"
        )
        db.session.add(doc)
        db.session.flush()

        ver_date = datetime.utcnow() - timedelta(days=idx)
        ver_id_code = f"VER-{str(idx).zfill(5)}"
        verification = Verification(
            document_id=doc.id,
            student_id=stud.id,
            college_id=d_meta["college"].id if d_meta["college"] else None,
            verification_source="STUDENT",
            final_status=d_meta["status"],
            ocr_status="PASSED",
            qr_status="PASSED" if d_meta["status"] == "AUTHENTICATED" else "NOT_APPLICABLE",
            forgery_status="PASSED" if d_meta["status"] == "AUTHENTICATED" else "FAILED",
            signature_status="PASSED" if d_meta["status"] == "AUTHENTICATED" else "NOT_APPLICABLE",
            stamp_status="PASSED" if d_meta["status"] == "AUTHENTICATED" else "NOT_APPLICABLE",
            metadata_status="PASSED",
            database_status="PASSED" if d_meta["college"] else "NOT_APPLICABLE",
            confidence_score=0.98 if d_meta["status"] == "AUTHENTICATED" else 0.35,
            verification_date=ver_date,
            verification_id=ver_id_code
        )
        db.session.add(verification)
        db.session.flush()

        # Generate Demo PDF Report
        rep_code = f"RPT-{str(idx).zfill(5)}"
        pdf_path = ReportService.generate_pdf_report(
            student_name=stud.full_name,
            student_id=stud.student_id,
            document_name=doc.original_filename,
            auth_status="Authenticated" if d_meta["status"] == "AUTHENTICATED" else "Not Authenticated",
            report_id=rep_code,
            verification_date=ver_date,
            doc_hash=doc_hash
        )

        report = Report(
            report_id=rep_code,
            verification_id=verification.id,
            student_id=stud.id,
            college_id=d_meta["college"].id if d_meta["college"] else None,
            verification_source="STUDENT",
            document_name=doc.original_filename,
            authentication_status=d_meta["status"],
            report_file_path=pdf_path,
            generated_at=ver_date
        )
        db.session.add(report)

        # Add Verification History
        v_hist = VerificationHistory(
            verification_id=verification.id,
            student_id=stud.id,
            college_id=d_meta["college"].id if d_meta["college"] else None,
            verification_source="STUDENT",
            document_id=doc.id,
            document_name=doc.original_filename,
            authentication_status=d_meta["status"],
            verification_date=ver_date,
            report_id=rep_code
        )
        db.session.add(v_hist)

        # Add Blockchain Record
        b_rec = BlockchainRecord(
            document_id=doc.id,
            verification_id=verification.id,
            document_hash=doc_hash,
            blockchain_tx_hash="0x" + hashlib.sha256(f"DEMO_TX_{doc_hash}".encode('utf-8')).hexdigest(),
            blockchain_network="Polygon POS Testnet",
            blockchain_status="CONFIRMED",
            timestamp=ver_date
        )
        db.session.add(b_rec)

    # 5. Create Sample Direct College Verifications for NIT101 and MUT202
    col_docs_meta = [
        {"college": colleges[0], "title": "State Board Higher Secondary Marksheet", "type": "Marksheet", "filename": "Walkin_Marksheet_NIT.pdf", "candidate": "Vikram Deshmukh", "status": "AUTHENTICATED"},
        {"college": colleges[0], "title": "Provisional Degree Certificate", "type": "Degree Certificate", "filename": "Direct_Degree_NIT.pdf", "candidate": "Ananya Sen", "status": "AUTHENTICATED"},
        {"college": colleges[1], "title": "Polytechnic Diploma Certificate", "type": "Diploma Certificate", "filename": "Diploma_Cert_MUT.pdf", "candidate": "Karan Joshi", "status": "AUTHENTICATED"}
    ]

    for cidx, cd in enumerate(col_docs_meta, start=101):
        col = cd["college"]
        dummy_content = f"DEMO_COLLEGE_DIRECT_VERIFICATION: {cd['title']} for {cd['candidate']} at {col.college_name}".encode('utf-8')
        doc_hash = hashlib.sha256(dummy_content).hexdigest()
        file_path = os.path.join(Config.UPLOAD_FOLDER, f"col_demo_{cd['filename']}")

        with open(file_path, "wb") as f:
            f.write(dummy_content)

        doc = Document(
            student_id=None,
            college_id=col.id,
            document_type=cd["type"],
            original_filename=cd["filename"],
            stored_filename=f"col_demo_{cd['filename']}",
            file_path=file_path,
            file_size=len(dummy_content),
            file_hash=doc_hash,
            mime_type="application/pdf"
        )
        db.session.add(doc)
        db.session.flush()

        ver_date = datetime.utcnow() - timedelta(days=cidx - 100)
        ver_id_code = f"VER-COL-{str(cidx).zfill(5)}"
        verification = Verification(
            document_id=doc.id,
            student_id=None,
            college_id=col.id,
            verification_source="COLLEGE",
            final_status=cd["status"],
            ocr_status="PASSED",
            qr_status="NOT_APPLICABLE",
            forgery_status="PASSED",
            signature_status="NOT_APPLICABLE",
            stamp_status="NOT_APPLICABLE",
            metadata_status="PASSED",
            database_status="NOT_APPLICABLE",
            confidence_score=0.98,
            verification_date=ver_date,
            verification_id=ver_id_code
        )
        db.session.add(verification)
        db.session.flush()

        rep_code = f"RPT-COL-{str(cidx).zfill(5)}"
        pdf_path = ReportService.generate_pdf_report(
            student_name=cd["candidate"],
            student_id="COLLEGE_DIRECT",
            document_name=doc.original_filename,
            auth_status="Authenticated",
            report_id=rep_code,
            verification_date=ver_date,
            doc_hash=doc_hash
        )

        report = Report(
            report_id=rep_code,
            verification_id=verification.id,
            student_id=None,
            college_id=col.id,
            verification_source="COLLEGE",
            document_name=doc.original_filename,
            authentication_status=cd["status"],
            report_file_path=pdf_path,
            generated_at=ver_date
        )
        db.session.add(report)

        v_hist = VerificationHistory(
            verification_id=verification.id,
            student_id=None,
            college_id=col.id,
            verification_source="COLLEGE",
            document_id=doc.id,
            document_name=doc.original_filename,
            authentication_status=cd["status"],
            verification_date=ver_date,
            report_id=rep_code
        )
        db.session.add(v_hist)

        b_rec = BlockchainRecord(
            document_id=doc.id,
            verification_id=verification.id,
            document_hash=doc_hash,
            blockchain_tx_hash="0x" + hashlib.sha256(f"DEMO_COL_TX_{doc_hash}".encode('utf-8')).hexdigest(),
            blockchain_network="Polygon POS Testnet",
            blockchain_status="CONFIRMED",
            timestamp=ver_date
        )
        db.session.add(b_rec)

    db.session.commit()
    print("Demo data seeded successfully with Colleges, Students, and Direct College Verification records.")
