import os
import sys
import json
import unittest
import pymupdf

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.user import User
from models.student import Student
from models.college import College
from models.document import Document
from models.verification import Verification
from models.verification_history import VerificationHistory
from models.report import Report
from models.blockchain_record import BlockchainRecord
from services.verification_service import verification_service
from flask_jwt_extended import create_access_token


class TestDocumentDeletionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def _create_authentic_pdf(self, file_path, student_name="Rahul Patil"):
        """Generates an authentic PDF that deterministically passes all 12 checks as AUTHENTICATED"""
        doc = pymupdf.open()
        page = doc.new_page()
        lines = [
            "SAVITRIBAI PHULE PUNE UNIVERSITY",
            "BACHELOR OF ENGINEERING DEGREE CERTIFICATE",
            f"This is to certify that {student_name} has been awarded the degree of",
            "Bachelor of Computer Engineering with First Class with Distinction",
            "Seat No: B190123456 | PRN: 71802345K",
            "Date of Issue: 15/06/2024",
            "Controller of Examinations",
            "Total Marks Obtained: 1250 / 1500 | Percentage: 83.33%"
        ]
        y = 50
        for line in lines:
            page.insert_text((50, y), line, fontsize=11)
            y += 20
        doc.save(file_path)
        doc.close()

    def test_01_student_delete_own_document_cascades_history_and_reports_and_zeros_dashboard(self):
        """
        Verify that when a student deletes their document:
        1. Document is permanently deleted from database.
        2. All associated verifications are permanently deleted.
        3. All associated verification history records are permanently deleted.
        4. All associated report records are permanently deleted.
        5. Physical uploaded file and generated PDF report on disk are removed.
        6. BlockchainRecord row is preserved with document_id and verification_id set to None.
        7. Student dashboard stats correctly update to zero when no documents remain.
        8. Refreshing stats confirms counts do not return.
        """
        student_user = User.query.filter_by(role="student").first()
        student = Student.query.filter_by(user_id=student_user.id).first()
        token = create_access_token(identity=str(student_user.id), additional_claims={"role": "student"})

        # Clean any pre-existing documents for this student to establish a pure baseline
        existing_docs = Document.query.filter_by(student_id=student.id).all()
        for ed in existing_docs:
            VerificationHistory.query.filter_by(document_id=ed.id).delete()
            vers = Verification.query.filter_by(document_id=ed.id).all()
            for v in vers:
                Report.query.filter_by(verification_id=v.id).delete()
                db.session.delete(v)
            db.session.delete(ed)
        db.session.commit()

        # Baseline check: 0 documents
        res_stats_0 = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats_0.status_code, 200)
        s0 = json.loads(res_stats_0.data)["stats"]
        self.assertEqual(s0["total_documents"], 0)
        self.assertEqual(s0["verified_documents"], 0)
        self.assertEqual(s0["pending_not_verified"], 0)
        self.assertEqual(s0["total_history"], 0)

        # Create authentic PDF document file
        upload_folder = self.app.config.get("UPLOAD_FOLDER", os.path.abspath("uploads"))
        os.makedirs(upload_folder, exist_ok=True)
        dummy_file_path = os.path.join(upload_folder, f"test_del_doc_{student.id}.pdf")
        self._create_authentic_pdf(dummy_file_path, student.full_name)

        # Create Document in DB
        doc = Document(
            student_id=student.id,
            document_type="Degree Certificate",
            original_filename="test_degree_deletion.pdf",
            stored_filename=os.path.basename(dummy_file_path),
            file_path=dummy_file_path,
            file_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
            file_size=os.path.getsize(dummy_file_path),
            mime_type="application/pdf"
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        # Run verification and generate report
        res, err = verification_service.verify_document(document_id=doc_id, user_id=student_user.id, role="student")
        self.assertIsNone(err)
        self.assertEqual(res["final_status"], "AUTHENTICATED")

        # Confirm all records and physical files exist
        ver_records = Verification.query.filter_by(document_id=doc_id).all()
        ver_ids = [v.id for v in ver_records]
        self.assertGreater(len(ver_records), 0)

        hist_records = VerificationHistory.query.filter_by(document_id=doc_id).all()
        self.assertGreater(len(hist_records), 0)

        rep_records = Report.query.filter(Report.verification_id.in_(ver_ids)).all()
        self.assertGreater(len(rep_records), 0)
        report_file_path = rep_records[0].report_file_path

        bc_records = BlockchainRecord.query.filter_by(document_id=doc_id).all()
        self.assertGreater(len(bc_records), 0)
        bc_record_id = bc_records[0].id

        self.assertTrue(os.path.exists(dummy_file_path))

        # Check dashboard counts BEFORE deletion
        res_before = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_before.status_code, 200)
        s_before = json.loads(res_before.data)["stats"]
        self.assertEqual(s_before["total_documents"], 1)
        self.assertEqual(s_before["verified_documents"], 1)
        self.assertEqual(s_before["pending_not_verified"], 0)
        self.assertGreaterEqual(s_before["total_history"], 1)

        # Perform deletion via DELETE /api/documents/<doc_id>
        resp = self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("success"))

        # 1. Assert Document is gone
        del_doc = db.session.get(Document, doc_id)
        self.assertIsNone(del_doc, "Document record should be permanently deleted")

        # 2. Assert Verifications are gone
        del_vers = Verification.query.filter_by(document_id=doc_id).all()
        self.assertEqual(len(del_vers), 0, "All verifications for document should be deleted")

        # 3. Assert Verification History records are gone
        del_hist = VerificationHistory.query.filter_by(document_id=doc_id).all()
        self.assertEqual(len(del_hist), 0, "All verification history for document should be deleted")

        # 4. Assert Reports are gone
        del_reps = Report.query.filter(Report.verification_id.in_(ver_ids)).all()
        self.assertEqual(len(del_reps), 0, "All reports for document should be deleted")

        # 5. Assert physical files on disk were removed
        self.assertFalse(os.path.exists(dummy_file_path), "Physical document file should be removed from disk")
        if report_file_path:
            self.assertFalse(os.path.exists(report_file_path), "Physical report PDF file should be removed from disk")

        # 6. Assert Blockchain record is preserved with document_id and verification_id set to None
        preserved_bc = db.session.get(BlockchainRecord, bc_record_id)
        self.assertIsNotNone(preserved_bc, "Blockchain record must be preserved for immutable audit log")
        self.assertIsNone(preserved_bc.document_id, "document_id reference should be dissociated (None)")
        self.assertIsNone(preserved_bc.verification_id, "verification_id reference should be dissociated (None)")
        self.assertEqual(preserved_bc.document_hash, res["sha256_hash"])

        # 7. Check dashboard counts AFTER deletion -> Must be zero
        res_after = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_after.status_code, 200)
        s_after = json.loads(res_after.data)["stats"]
        self.assertEqual(s_after["total_documents"], 0, "Total documents must update to 0")
        self.assertEqual(s_after["verified_documents"], 0, "Verified documents must update to 0")
        self.assertEqual(s_after["pending_not_verified"], 0, "Pending/Not verified must update to 0")
        self.assertEqual(s_after["total_history"], 0, "Verification history must update to 0")

        # 8. Refresh check: re-fetch and verify counts do not return
        res_refresh = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_refresh.status_code, 200)
        s_refresh = json.loads(res_refresh.data)["stats"]
        self.assertEqual(s_refresh["total_documents"], 0)
        self.assertEqual(s_refresh["verified_documents"], 0)
        self.assertEqual(s_refresh["pending_not_verified"], 0)
        self.assertEqual(s_refresh["total_history"], 0)

    def test_02_multiple_documents_deletion_isolation(self):
        """
        Verify that when a user has multiple documents:
        1. Deleting one document removes only its exclusive records.
        2. Dashboard counts correctly recalculate for the remaining documents.
        3. The remaining document and its verification history/reports remain intact.
        4. Deleting the remaining document zeroes the counts completely.
        """
        student_user = User.query.filter_by(role="student").first()
        student = Student.query.filter_by(user_id=student_user.id).first()
        token = create_access_token(identity=str(student_user.id), additional_claims={"role": "student"})

        # Clean pre-existing documents
        existing_docs = Document.query.filter_by(student_id=student.id).all()
        for ed in existing_docs:
            VerificationHistory.query.filter_by(document_id=ed.id).delete()
            vers = Verification.query.filter_by(document_id=ed.id).all()
            for v in vers:
                Report.query.filter_by(verification_id=v.id).delete()
                db.session.delete(v)
            db.session.delete(ed)
        db.session.commit()

        upload_folder = self.app.config.get("UPLOAD_FOLDER", os.path.abspath("uploads"))
        os.makedirs(upload_folder, exist_ok=True)

        # Create Document A (Authentic Degree Certificate)
        path_a = os.path.join(upload_folder, f"doc_a_{student.id}.pdf")
        self._create_authentic_pdf(path_a, student.full_name)

        doc_a = Document(
            student_id=student.id,
            document_type="Degree Certificate",
            original_filename="doc_a.pdf",
            stored_filename=os.path.basename(path_a),
            file_path=path_a,
            file_hash="aaaabbbbccccdddd1111222233334444aaaabbbbccccdddd1111222233334444",
            file_size=os.path.getsize(path_a),
            mime_type="application/pdf"
        )
        db.session.add(doc_a)

        # Create Document B (Marksheet - left unverified)
        path_b = os.path.join(upload_folder, f"doc_b_{student.id}.pdf")
        with open(path_b, "wb") as f:
            f.write(b"%PDF-1.4 Content of Document B")

        doc_b = Document(
            student_id=student.id,
            document_type="10th Marksheet",
            original_filename="doc_b.pdf",
            stored_filename=os.path.basename(path_b),
            file_path=path_b,
            file_hash="bbbbccccddddaaaa2222333344441111bbbbccccddddaaaa2222333344441111",
            file_size=len(b"%PDF-1.4 Content of Document B"),
            mime_type="application/pdf"
        )
        db.session.add(doc_b)
        db.session.commit()

        doc_a_id = doc_a.id
        doc_b_id = doc_b.id

        # Verify Document A (Passed -> AUTHENTICATED)
        res_a, err_a = verification_service.verify_document(document_id=doc_a_id, user_id=student_user.id, role="student")
        self.assertIsNone(err_a)
        self.assertEqual(res_a["final_status"], "AUTHENTICATED")

        # Document B remains unverified (Pending / Not Verified)

        # Check dashboard stats: Total: 2, Verified: 1, Pending/Not Verified: 1
        res_stats = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats.status_code, 200)
        s = json.loads(res_stats.data)["stats"]
        self.assertEqual(s["total_documents"], 2)
        self.assertEqual(s["verified_documents"], 1)
        self.assertEqual(s["pending_not_verified"], 1)
        self.assertEqual(s["total_history"], 1)

        # Delete Document A
        resp_del_a = self.client.delete(f"/api/documents/{doc_a_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp_del_a.status_code, 200)

        # Confirm Document A file is gone, Document B file remains
        self.assertFalse(os.path.exists(path_a))
        self.assertTrue(os.path.exists(path_b))

        # Check dashboard stats: Total: 1, Verified: 0, Pending/Not Verified: 1, History: 0
        res_stats_after_a = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats_after_a.status_code, 200)
        s_after_a = json.loads(res_stats_after_a.data)["stats"]
        self.assertEqual(s_after_a["total_documents"], 1, "Only Document B should remain")
        self.assertEqual(s_after_a["verified_documents"], 0, "No verified documents should remain")
        self.assertEqual(s_after_a["pending_not_verified"], 1, "Document B should count as pending/unverified")
        self.assertEqual(s_after_a["total_history"], 0, "Document A's history should be gone")

        # Delete Document B
        resp_del_b = self.client.delete(f"/api/documents/{doc_b_id}", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp_del_b.status_code, 200)

        # Check dashboard stats: Total: 0, Verified: 0, Pending/Not Verified: 0, History: 0
        res_stats_after_b = self.client.get("/api/student/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_stats_after_b.status_code, 200)
        s_after_b = json.loads(res_stats_after_b.data)["stats"]
        self.assertEqual(s_after_b["total_documents"], 0)
        self.assertEqual(s_after_b["verified_documents"], 0)
        self.assertEqual(s_after_b["pending_not_verified"], 0)
        self.assertEqual(s_after_b["total_history"], 0)

    def test_03_institution_direct_document_deletion_and_dashboard_stats(self):
        """
        Verify Institution direct document upload, verification, and deletion:
        1. Institution uploads direct document and verifies it.
        2. Dashboard reflects the direct document and its verified status.
        3. Institution deletes the direct document.
        4. Exclusive records and files are removed.
        5. College dashboard direct document counts update to 0.
        6. Connected students count is preserved.
        """
        college_user = User.query.filter_by(role="college").first()
        college = College.query.filter_by(user_id=college_user.id).first()
        college_token = create_access_token(identity=str(college_user.id), additional_claims={"role": "college"})

        # Clean existing direct documents for this college
        existing_direct = Document.query.filter_by(college_id=college.id, student_id=None).all()
        for ed in existing_direct:
            VerificationHistory.query.filter_by(document_id=ed.id).delete()
            vers = Verification.query.filter_by(document_id=ed.id).all()
            for v in vers:
                Report.query.filter_by(verification_id=v.id).delete()
                db.session.delete(v)
            db.session.delete(ed)
        db.session.commit()

        upload_folder = self.app.config.get("UPLOAD_FOLDER", os.path.abspath("uploads"))
        os.makedirs(upload_folder, exist_ok=True)
        direct_path = os.path.join(upload_folder, f"direct_col_{college.id}.pdf")
        self._create_authentic_pdf(direct_path, "Direct Walk-in Candidate")

        # Create direct Document in DB
        direct_doc = Document(
            student_id=None,
            college_id=college.id,
            document_type="Degree Certificate",
            original_filename="walkin_candidate_degree.pdf",
            stored_filename=os.path.basename(direct_path),
            file_path=direct_path,
            file_hash="9999888877776666555544443333222211110000aaaabbbbccccddddaaaabbbb",
            file_size=os.path.getsize(direct_path),
            mime_type="application/pdf"
        )
        db.session.add(direct_doc)
        db.session.commit()
        doc_id = direct_doc.id

        # Verify direct document
        res, err = verification_service.verify_document(
            document_id=doc_id,
            user_id=college_user.id,
            role="college",
            candidate_name="Direct Walk-in Candidate"
        )
        self.assertIsNone(err)
        self.assertEqual(res["final_status"], "AUTHENTICATED")

        # Check college dashboard before deletion
        res_before = self.client.get("/api/college/dashboard-stats", headers={"Authorization": f"Bearer {college_token}"})
        self.assertEqual(res_before.status_code, 200)
        s_before = json.loads(res_before.data)["stats"]
        self.assertEqual(s_before["total_documents"], 1)
        self.assertEqual(s_before["verified_documents"], 1)
        connected_students_before = s_before["linked_students"]

        # Delete direct document
        resp_del = self.client.delete(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {college_token}"})
        self.assertEqual(resp_del.status_code, 200)

        # Confirm DB record and file removed
        self.assertIsNone(db.session.get(Document, doc_id))
        self.assertFalse(os.path.exists(direct_path))

        # Check college dashboard after deletion -> Total: 0, Verified: 0, Connected students preserved
        res_after = self.client.get("/api/college/dashboard-stats", headers={"Authorization": f"Bearer {college_token}"})
        self.assertEqual(res_after.status_code, 200)
        s_after = json.loads(res_after.data)["stats"]
        self.assertEqual(s_after["total_documents"], 0, "Direct documents must update to 0")
        self.assertEqual(s_after["verified_documents"], 0, "Verified direct documents must update to 0")
        self.assertEqual(s_after["linked_students"], connected_students_before, "Connected students count must be preserved")

    def test_04_institution_cannot_delete_student_document(self):
        """Ensure institutions are strictly forbidden from deleting student-owned documents"""
        student_user = User.query.filter_by(role="student").first()
        student = Student.query.filter_by(user_id=student_user.id).first()
        college_user = User.query.filter_by(role="college").first()
        college = College.query.filter_by(user_id=college_user.id).first()

        college_token = create_access_token(identity=str(college_user.id), additional_claims={"role": "college"})

        # Create a document owned by the student
        doc = Document(
            student_id=student.id,
            college_id=college.id,
            document_type="10th Marksheet",
            original_filename="student_marksheet.pdf",
            stored_filename="stu_ms.pdf",
            file_path="uploads/stu_ms.pdf",
            file_hash="99887766554433221100aabbccddeeff99887766554433221100aabbccddeeff",
            file_size=2048,
            mime_type="application/pdf"
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        # College attempts to delete student document
        resp = self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {college_token}"}
        )
        self.assertEqual(resp.status_code, 403, "College must receive 403 Forbidden when attempting to delete student document")

        # Clean up test document
        db.session.delete(doc)
        db.session.commit()

    def test_05_student_cannot_delete_another_students_document(self):
        """Ensure students cannot delete documents belonging to other students"""
        students = Student.query.limit(2).all()
        if len(students) < 2:
            self.skipTest("Need at least 2 students to test cross-student deletion")

        s1, s2 = students[0], students[1]
        s1_user = db.session.get(User, s1.user_id)
        s1_token = create_access_token(identity=str(s1_user.id), additional_claims={"role": "student"})

        # Create doc for s2
        doc = Document(
            student_id=s2.id,
            document_type="Bonafide Certificate",
            original_filename="s2_bonafide.pdf",
            stored_filename="s2_bona.pdf",
            file_path="uploads/s2_bona.pdf",
            file_hash="1234567890123456789012345678901234567890123456789012345678901234",
            file_size=1024,
            mime_type="application/pdf"
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        # s1 attempts to delete s2's document
        resp = self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {s1_token}"}
        )
        self.assertEqual(resp.status_code, 403, "Student must receive 403 Forbidden when attempting to delete another student's document")

        # Clean up
        db.session.delete(doc)
        db.session.commit()


if __name__ == "__main__":
    unittest.main()
