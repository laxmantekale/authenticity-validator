import os
import io
import sys
import unittest
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None
from PIL import Image

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.engine import verification_engine
from verification.rule_engine.rule_engine import rule_engine
from verification.rule_engine.classification_rules import ClassificationRules
from verification.rule_engine.date_rules import DateRules
from verification.rule_engine.field_rules import FieldRules
from verification.rule_engine.identifier_rules import IdentifierRules
from verification.rule_engine.issuer_rules import IssuerRules
from verification.rule_engine.metadata_rules import MetadataRules

class TestVerificationEngineSuite(unittest.TestCase):
    def setUp(self):
        self.scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_docs"))
        os.makedirs(self.scratch_dir, exist_ok=True)

    def create_pdf(self, filename: str, text_lines: list, meta: dict = None) -> str:
        path = os.path.join(self.scratch_dir, filename)
        doc = pymupdf.open()
        page = doc.new_page()
        y = 50
        for line in text_lines:
            page.insert_text((50, y), line, fontsize=11)
            y += 20
        if meta:
            doc.set_metadata(meta)
        doc.save(path)
        doc.close()
        return path

    def test_01_academic_degree_authenticated(self):
        """Test standard authentic University Degree Certificate"""
        pdf_path = self.create_pdf(
            "degree_cert.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "BACHELOR OF ENGINEERING DEGREE CERTIFICATE",
                "This is to certify that Rahul Sharma has been awarded the degree of",
                "Bachelor of Computer Engineering with First Class with Distinction",
                "Seat No: B190123456 | PRN: 71802345K",
                "Date of Issue: 15/06/2024",
                "Controller of Examinations",
                "Total Marks Obtained: 1250 / 1500 | Percentage: 83.33%"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["checks"]["text_extraction"], "PASSED")
        self.assertEqual(res["checks"]["document_classification"], "PASSED")
        self.assertEqual(res["checks"]["document_integrity"], "PASSED")
        self.assertEqual(res["doc_type_detected"], "Degree Certificate")
        self.assertEqual(res["category"], "Academic")

    def test_02_impossible_calendar_date_suspicious(self):
        """Test document with impossible calendar date (31/02/2025)"""
        pdf_path = self.create_pdf(
            "impossible_date.pdf",
            [
                "MAHARASHTRA STATE BOARD OF SECONDARY EDUCATION",
                "HIGHER SECONDARY CERTIFICATE MARKSHEET",
                "Candidate Name: Rajesh Kumar",
                "Seat Number: M102938",
                "Date of Issue: 31/02/2025", # Impossible date
                "Total Marks: 450 / 600",
                "Percentage: 75.00%"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["date_consistency"], "SUSPICIOUS")

    def test_03_impossible_marks_obtained_greater_than_max(self):
        """Test marksheet with marks obtained > maximum marks (520/500)"""
        pdf_path = self.create_pdf(
            "invalid_marks.pdf",
            [
                "CENTRAL BOARD OF SECONDARY EDUCATION",
                "ALL INDIA SECONDARY SCHOOL EXAMINATION",
                "Candidate: Amit Patel",
                "Roll No: 12345678",
                "Date: 12/05/2023",
                "Total Marks Obtained: 520 / 500", # Impossible marks
                "Percentage: 104%"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_04_percentage_arithmetic_mismatch_suspicious(self):
        """Test marksheet with arithmetic percentage contradiction (400/500 is 80%, but printed 95%)"""
        pdf_path = self.create_pdf(
            "pct_mismatch.pdf",
            [
                "UNIVERSITY OF MUMBAI",
                "STATEMENT OF MARKS - SEMESTER VI",
                "Candidate: Priya Verma",
                "Seat No: MU892019",
                "Marks Obtained: 400 Out of 500",
                "Percentage: 95.00%", # Mismatch: 400/500 = 80% != 95%
                "Date: 20/07/2023"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_05_photoshop_metadata_suspicious(self):
        """Test document edited with Photoshop metadata"""
        pdf_path = self.create_pdf(
            "photoshop_tampered.pdf",
            [
                "GOVERNMENT OF MAHARASHTRA",
                "INCOME CERTIFICATE",
                "Application No: REV/2024/99182",
                "Date: 10/01/2024",
                "Annual Income: Rs. 1,50,000"
            ],
            meta={"creator": "Adobe Photoshop 2024 (Windows)", "producer": "Adobe PDF Library 17.0"}
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["metadata_analysis"], "SUSPICIOUS")

    def test_06_identity_pan_card_authenticated(self):
        """Test valid PAN Card format"""
        pdf_path = self.create_pdf(
            "pan_card.pdf",
            [
                "INCOME TAX DEPARTMENT - GOVT OF INDIA",
                "PERMANENT ACCOUNT NUMBER CARD",
                "Name: SURESH MENON",
                "Father's Name: KESHAV MENON",
                "Date of Birth: 14/08/1995",
                "PAN: ABCPS1234F" # Valid PAN format with P for Individual
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "PAN Card")
        self.assertEqual(res["checks"]["official_verification"], "NOT_VERIFIED")

    def test_07_unknown_document_not_verified(self):
        """Test unrecognized document format"""
        pdf_path = self.create_pdf(
            "random_grocery_list.pdf",
            [
                "Shopping List for Sunday",
                "Apples 1kg",
                "Milk 2 packets",
                "Bread 1 loaf",
                "Eggs 1 dozen"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "NOT_VERIFIED")
        self.assertEqual(res["doc_type_detected"], "Unknown Document")
        self.assertEqual(res["checks"]["document_classification"], "NOT_VERIFIED")

    def test_08_corrupted_file_verification_failed(self):
        """Test corrupted or empty file"""
        corrupted_path = os.path.join(self.scratch_dir, "corrupted.pdf")
        with open(corrupted_path, "wb") as f:
            f.write(b"CORRUPTED_NON_PDF_BYTES_12345")
        res = verification_engine.run_full_pipeline(corrupted_path)
        self.assertEqual(res["final_status"], "VERIFICATION_FAILED")
        self.assertEqual(res["checks"]["document_integrity"], "FAILED")

    def test_09_multi_page_pdf_extraction(self):
        """Test multi-page PDF extraction combining information across pages"""
        path = os.path.join(self.scratch_dir, "multipage_marksheet.pdf")
        doc = pymupdf.open()
        # Page 1: University Header and Candidate Info
        p1 = doc.new_page()
        p1.insert_text((50, 50), "UNIVERSITY OF MUMBAI", fontsize=12)
        p1.insert_text((50, 80), "STATEMENT OF MARKS - SEMESTER V", fontsize=11)
        p1.insert_text((50, 110), "Candidate Name: Sneha Patil", fontsize=10)
        p1.insert_text((50, 140), "Seat No: MU40291 | PRN: 20200164009988", fontsize=10)
        
        # Page 2: Marks, CGPA, and Result
        p2 = doc.new_page()
        p2.insert_text((50, 50), "SUBJECT WISE PERFORMANCE RECORD", fontsize=11)
        p2.insert_text((50, 80), "Total Marks Obtained: 510 / 600", fontsize=10)
        p2.insert_text((50, 110), "Percentage: 85.00% | CGPA: 8.90", fontsize=10)
        p2.insert_text((50, 140), "Result: First Class with Distinction", fontsize=10)
        p2.insert_text((50, 170), "Date of Issue: 22/11/2023", fontsize=10)
        doc.save(path)
        doc.close()

        res = verification_engine.run_full_pipeline(path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "Semester Marksheet")
        self.assertEqual(res["category"], "Academic")
        self.assertGreaterEqual(res["classification_confidence"], 80.0)

    def test_10_ssc_10th_marksheet_classification(self):
        """Test Class 10 / SSC Marksheet automatic identification"""
        pdf_path = self.create_pdf(
            "ssc_10th_doc.pdf",
            [
                "MAHARASHTRA STATE BOARD OF SECONDARY EDUCATION",
                "SECONDARY SCHOOL CERTIFICATE EXAMINATION",
                "STATEMENT OF MARKS - CLASS X",
                "Candidate Name: Aditya Joshi",
                "Seat No: A091823",
                "Date of Birth: 10/05/2006",
                "Total Marks Obtained: 475 / 500",
                "Percentage: 95.00%",
                "Date: 17/06/2022"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "10th Marksheet")
        self.assertEqual(res["category"], "Academic")
        self.assertGreaterEqual(res["classification_confidence"], 85.0)

    def test_11_hsc_12th_marksheet_classification(self):
        """Test Class 12 / HSC Marksheet automatic identification"""
        pdf_path = self.create_pdf(
            "hsc_12th_doc.pdf",
            [
                "MAHARASHTRA STATE BOARD OF SECONDARY AND HIGHER SECONDARY EDUCATION",
                "HIGHER SECONDARY CERTIFICATE EXAMINATION",
                "STATEMENT OF MARKS - CLASS XII",
                "Stream: Science | Physics | Chemistry | Mathematics",
                "Candidate Name: Tanvi Kulkarni",
                "Seat No: H192837",
                "Total Marks: 540 / 600",
                "Percentage: 90.00%",
                "Date: 25/05/2024"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "12th Marksheet")
        self.assertEqual(res["category"], "Academic")

    def test_12_provisional_degree_certificate(self):
        """Test Provisional Degree Certificate automatic identification"""
        pdf_path = self.create_pdf(
            "provisional_degree.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "PROVISIONAL DEGREE CERTIFICATE",
                "This is to certify that Vikrant Deshmukh has passed the examination for the degree of",
                "Bachelor of Technology in Information Technology in the year 2024",
                "Eligible for the award of degree at the next Convocation",
                "PRN No: 72001928K | Date: 18/07/2024",
                "Controller of Examinations"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "Provisional Degree Certificate")
        self.assertEqual(res["category"], "Academic")

    def test_13_aadhaar_card_classification(self):
        """Test Aadhaar Card identification with masked number format"""
        pdf_path = self.create_pdf(
            "aadhaar_identity.pdf",
            [
                "UNIQUE IDENTIFICATION AUTHORITY OF INDIA",
                "GOVERNMENT OF INDIA",
                "MERA AADHAAR MERI PEHCHAN",
                "Name: Anjali Rane",
                "DOB: 12/03/1998 | Gender: Female",
                "Aadhaar No: XXXX XXXX 8912"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "Aadhaar Card")
        self.assertEqual(res["category"], "Identity")

    def test_14_government_7_12_extract(self):
        """Test Maharashtra 7/12 Land Record identification"""
        pdf_path = self.create_pdf(
            "satbara_record.pdf",
            [
                "GOVERNMENT OF MAHARASHTRA - REVENUE DEPARTMENT",
                "VILLAGE FORM NO. 7 - 7/12 EXTRACT (SATBARA)",
                "ADHIKAR ABHILEKH PATRAK",
                "Gat No: 142 / Survey No: 88",
                "Total Area: 1.25 Hector | Aakar: Rs 12.50",
                "Date: 05/01/2024"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["doc_type_detected"], "7/12 Extract")
        self.assertEqual(res["category"], "Property")

    def test_15_calibrated_confidence_scoring(self):
        """Verify dynamic calibrated confidence calculation across evidence points"""
        # Genuine degree certificate with multiple corroborating signals
        pdf_path = self.create_pdf(
            "high_confidence_degree.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "BACHELOR OF TECHNOLOGY DEGREE CERTIFICATE",
                "Hereby confers on Kunal Mehta the Degree of Bachelor of Technology",
                "First Class with Distinction | Convocation held on 15/02/2024",
                "Under the Seal of the University | Vice-Chancellor",
                "PRN: 71928371M | Seat No: T190028"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertGreaterEqual(res["classification_confidence"], 90.0)
        self.assertLessEqual(res["classification_confidence"], 99.0)

    def test_16_verification_status_clean_formatting(self):
        """Verify model clean representations for all supported final statuses"""
        from models.verification import Verification
        
        status_map = {
            "AUTHENTICATED": "Authenticated",
            "SUSPICIOUS": "Suspicious",
            "NOT_VERIFIED": "Not Verified",
            "VERIFICATION_FAILED": "Verification Failed",
            "IN_PROGRESS": "In Progress",
            "PENDING": "In Progress",
            "NOT_AUTHENTICATED": "Not Authenticated"
        }
        for raw, expected in status_map.items():
            v = Verification(final_status=raw)
            self.assertEqual(v.final_status_clean, expected)
            self.assertEqual(v.overall_status, expected)

if __name__ == "__main__":
    unittest.main()


