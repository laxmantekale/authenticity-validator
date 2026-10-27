import os
import io
import sys
import unittest
import numpy as np
import cv2
from PIL import Image

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

from verification.ocr_verifier import ocr_verifier
from verification.rule_engine.classification_rules import ClassificationRules
from verification.rule_engine.field_rules import FieldRules
from verification.rule_engine.date_rules import DateRules
from verification.engine import verification_engine
from services.report_service import generate_pdf_report
from models.report import Report
from models.verification import Verification

class TestVerificationAccuracyAndReport(unittest.TestCase):
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

    def test_01_image_preprocessing_blur_and_deskew(self):
        """Test OCR preprocessor blur detection and deskewing functions"""
        # Create a sharp test image
        sharp_img = np.zeros((200, 200), dtype=np.uint8)
        cv2.rectangle(sharp_img, (50, 50), (150, 150), 255, -1)
        is_blurry, var = ocr_verifier.detect_blur(sharp_img, threshold=50.0)
        self.assertFalse(is_blurry)
        self.assertGreater(var, 50.0)

        # Create a blurred image
        blurred_img = cv2.GaussianBlur(sharp_img, (25, 25), 0)
        is_blurry, var = ocr_verifier.detect_blur(blurred_img, threshold=100.0)
        self.assertTrue(is_blurry)

        # Test deskewing
        rotated_img = np.zeros((300, 300), dtype=np.uint8)
        cv2.putText(rotated_img, "VERIFICATION ENGINE", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
        deskewed, angle = ocr_verifier.deskew_image(rotated_img)
        self.assertEqual(deskewed.shape, rotated_img.shape)

    def test_02_classification_without_filename_bias(self):
        """Classification must rely on content evidence, not filename alias"""
        # Filename says 'degree_cert.pdf', but content is a generic receipt
        pdf_path = self.create_pdf(
            "degree_cert_spoofed.pdf",
            [
                "SUPERMARKET RETAIL STORE",
                "RECEIPT NO: 994821",
                "Item 1: Organic Milk - Rs 60",
                "Item 2: Whole Wheat Bread - Rs 45",
                "Total Amount: Rs 105",
                "Thank you for shopping with us!"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        # Content must not be classified as Degree Certificate
        self.assertNotEqual(res["doc_type_detected"], "Degree Certificate")
        self.assertEqual(res["final_status"], "NOT_VERIFIED")
        self.assertLessEqual(res["classification_confidence"], 30.0)

    def test_03_unknown_document_safe_guardrail(self):
        """Unrecognized document must return UNKNOWN_DOCUMENT and NOT_VERIFIED, never labeled forged"""
        pdf_path = self.create_pdf(
            "recipe_notes.pdf",
            [
                "Grandma's Cookie Recipe",
                "Ingredients: Flour, Sugar, Butter, Chocolate chips",
                "Bake at 350 degrees F for 12 minutes."
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "NOT_VERIFIED")
        self.assertIn("Unknown Document", res["doc_type_detected"])
        self.assertIn("NOT_VERIFIED", res["checks"]["document_classification"])
        self.assertLessEqual(res["classification_confidence"], 30.0)
        # Explanation must clearly state unverified, not forged
        self.assertIn("A result of NOT_VERIFIED does not by itself establish that the document is fraudulent", res["explanation"])

    def test_04_impossible_numerical_marks_suspicious(self):
        """Marks obtained exceeding total marks must trigger SUSPICIOUS"""
        pdf_path = self.create_pdf(
            "excess_marks.pdf",
            [
                "CENTRAL BOARD OF SECONDARY EDUCATION",
                "ALL INDIA SENIOR SCHOOL CERTIFICATE EXAMINATION",
                "STATEMENT OF MARKS - CLASS XII",
                "Candidate: Vikram Malhotra",
                "Roll No: 1209384",
                "Marks Obtained: 650 / 600",
                "Percentage: 108%",
                "Date: 12/05/2023"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_05_arithmetic_percentage_discrepancy_suspicious(self):
        """Percentage inconsistent with marks obtained triggers SUSPICIOUS"""
        pdf_path = self.create_pdf(
            "fake_distinction_percentage.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "STATEMENT OF GRADES - SEMESTER IV",
                "Candidate: Rohan Joshi",
                "Seat No: T1900192",
                "Marks Obtained: 300 / 600", # Actual 50%
                "Percentage: 92.50%",       # Fabricated 92.50%
                "Date: 15/06/2023"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_06_date_chronology_issue_after_expiry_suspicious(self):
        """Document with issue date strictly after expiry date triggers SUSPICIOUS"""
        pdf_path = self.create_pdf(
            "chronology_anomaly.pdf",
            [
                "REPUBLIC OF INDIA",
                "PASSPORT",
                "Holder Name: Amit Kulkarni",
                "Passport No: Z9102938",
                "Date of Issue: 20/05/2025",
                "Date of Expiry: 10/01/2022" # Expired before issue!
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["date_consistency"], "SUSPICIOUS")

    def test_07_missing_qr_and_signature_not_penalized(self):
        """Documents lacking QR code or digital signature must mark checks NOT_APPLICABLE without failure"""
        pdf_path = self.create_pdf(
            "clean_marksheet_no_qr.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "STATEMENT OF MARKS - SEMESTER VIII",
                "Candidate: Neha Deshpande",
                "Seat No: B19011928 | PRN: 71900281F",
                "Marks: 1100 / 1500 | Percentage: 73.33%",
                "Result: First Class",
                "Date of Issue: 20/06/2024"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["checks"]["qr_verification"], "NOT_APPLICABLE")
        self.assertEqual(res["checks"]["digital_signature"], "NOT_APPLICABLE")
        self.assertEqual(res["checks"]["barcode_verification"], "NOT_APPLICABLE")

    def test_08_multidimensional_confidence_scores(self):
        """Verify decomposition into classification confidence, extraction quality, and evidence strength"""
        pdf_path = self.create_pdf(
            "valid_degree.pdf",
            [
                "SAVITRIBAI PHULE PUNE UNIVERSITY",
                "BACHELOR OF ENGINEERING DEGREE CERTIFICATE",
                "Rahul Sharma has been awarded the degree of Bachelor of Engineering",
                "Seat No: B190123456 | PRN: 71802345K",
                "Date of Issue: 15/06/2024",
                "Controller of Examinations"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf_path)
        self.assertIn("classification_confidence", res)
        self.assertIn("extraction_quality", res)
        self.assertIn("evidence_strength", res)
        self.assertGreater(res["classification_confidence"], 70.0)
        self.assertGreater(res["extraction_quality"], 50.0)

    def test_09_reportlab_multisection_pdf_generation(self):
        """Test professional publication-grade ReportLab PDF generation with Sections A-I and SHA-256 seal"""
        dummy_evidence = {
            "classification_confidence": 94.5,
            "extraction_quality": 88.0,
            "evidence_strength": "Strong (Deterministic Multi-Signal Consistency)",
            "ocr_metrics": {"page_count": 1, "char_count": 450, "warnings": []},
            "findings": {
                "confirmed": ["University issuer confirmed", "PRN identifier validated"],
                "warnings": [],
                "checks_not_performed": ["Official registry API not configured"],
                "technical_limitations": []
            },
            "recommended_next_steps": [
                "Credential verified for academic admission processing.",
                "Maintain digital PDF certificate for student records."
            ],
            "checks_detail": [
                {
                    "key": "text_extraction",
                    "name": "Text Extraction",
                    "status": "PASSED",
                    "short_explanation": "Extracted 450 characters across 1 page(s).",
                    "limitations": "Digital text stream direct extraction."
                },
                {
                    "key": "document_classification",
                    "name": "Document Classification",
                    "status": "PASSED",
                    "short_explanation": "Classified as Degree Certificate with 94.5% match.",
                    "limitations": "Multi-signal pattern evaluation."
                },
                {
                    "key": "required_fields",
                    "name": "Required Fields",
                    "status": "PASSED",
                    "short_explanation": "All mandatory fields detected.",
                    "limitations": "Deterministic field check."
                },
                {
                    "key": "field_consistency",
                    "name": "Field Consistency",
                    "status": "PASSED",
                    "short_explanation": "Numerical marks consistent.",
                    "limitations": "Arithmetic validation."
                },
                {
                    "key": "date_consistency",
                    "name": "Date Consistency",
                    "status": "PASSED",
                    "short_explanation": "Date chronology valid.",
                    "limitations": "Calendar verification."
                },
                {
                    "key": "identifier_validation",
                    "name": "Identifier Validation",
                    "status": "PASSED",
                    "short_explanation": "PRN and Seat numbers valid.",
                    "limitations": "Format regex matching."
                },
                {
                    "key": "qr_verification",
                    "name": "QR Verification",
                    "status": "NOT_APPLICABLE",
                    "short_explanation": "No QR code detected.",
                    "limitations": "Standard for non-digital certificate format."
                },
                {
                    "key": "barcode_verification",
                    "name": "Barcode Verification",
                    "status": "NOT_APPLICABLE",
                    "short_explanation": "No barcode detected.",
                    "limitations": "Optional feature."
                },
                {
                    "key": "digital_signature",
                    "name": "Digital Signature",
                    "status": "NOT_APPLICABLE",
                    "short_explanation": "No cryptographic signature embedded.",
                    "limitations": "Typical for scanned paper copies."
                },
                {
                    "key": "document_integrity",
                    "name": "Document Integrity",
                    "status": "PASSED",
                    "short_explanation": "SHA-256 seal generated.",
                    "limitations": "Local ledger integrity check."
                },
                {
                    "key": "metadata_analysis",
                    "name": "Metadata Analysis",
                    "status": "PASSED",
                    "short_explanation": "Clean document metadata.",
                    "limitations": "PDF header inspection."
                },
                {
                    "key": "official_verification",
                    "name": "Official Verification",
                    "status": "NOT_VERIFIED",
                    "short_explanation": "Official registry not connected.",
                    "limitations": "Requires institution registry key."
                }
            ],
            "document_info": {
                "document_title": "Degree Certificate",
                "holder_name": "Rahul Sharma",
                "document_identifier": "PRN: 71802345K",
                "issuer_institution": "Savitribai Phule Pune University",
                "issue_date": "15/06/2024",
                "expiry_date": "Permanent",
                "number_of_pages": 1,
                "file_format": "PDF",
                "file_size": "24.5 KB",
                "sha256_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0"
            }
        }

        from datetime import datetime
        pdf_path = generate_pdf_report(
            student_name="Rahul Sharma",
            student_id="STU-2026-001",
            document_name="bachelor_degree.pdf",
            auth_status="AUTHENTICATED",
            report_id="RPT-TEST-2026-001",
            verification_date=datetime.now(),
            doc_hash="a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            doc_type="Degree Certificate",
            checks={c["key"]: c["status"] for c in dummy_evidence["checks_detail"]},
            full_verification_data=dummy_evidence
        )

        self.assertTrue(os.path.exists(pdf_path))
        file_size = os.path.getsize(pdf_path)
        self.assertGreater(file_size, 4000) # Valid multi-section PDF

        # Verify PDF contents with PyMuPDF
        pdf = pymupdf.open(pdf_path)
        self.assertGreaterEqual(len(pdf), 1)
        full_text = ""
        for page in pdf:
            full_text += page.get_text()
        pdf.close()

        self.assertIn("AUTHENTICATION VALIDATOR", full_text)
        self.assertIn("RPT-TEST-2026-001", full_text)
        self.assertIn("AUTHENTICATED", full_text)
        self.assertIn("MODULAR VERIFICATION CHECKS", full_text)
        self.assertIn("FINDINGS & TECHNICAL LIMITATIONS", full_text)

    def test_10_report_model_to_full_details_serialization(self):
        """Test report model full serialization with Section A-I schema"""
        import json
        rep = Report(
            report_id="RPT-2026-TEST99",
            verification_id=101,
            student_id=303,
            document_name="marksheet.pdf",
            report_file_path="reports/test.pdf",
            authentication_status="AUTHENTICATED"
        )
        rep.report_data = json.dumps({
            "section_a": {"report_id": "RPT-2026-TEST99"},
            "section_b": {"final_status": "AUTHENTICATED", "classification_confidence": 92.0},
            "section_c": {"document_title": "Semester Marksheet", "holder_name": "Pooja Sharma"},
            "section_d": [{"name": "Text Extraction", "status": "PASSED"}],
            "section_e": {"confirmed": ["Valid marks"]},
            "section_f": "All checks passed.",
            "section_g": ["Admit student."],
            "section_h": {"file_hash": "abc123hash"},
            "section_i": {"disclaimer": "Official educational evaluation."}
        })

        details = rep.to_full_details()
        self.assertIn("section_a", details)
        self.assertIn("section_b", details)
        self.assertIn("section_c", details)
        self.assertIn("section_d", details)
        self.assertIn("section_e", details)
        self.assertIn("section_f", details)
        self.assertIn("section_g", details)
        self.assertIn("section_h", details)
        self.assertIn("section_i", details)
        self.assertEqual(details["section_a"]["report_id"], "RPT-2026-TEST99")
        self.assertEqual(details["section_b"]["final_status"], "AUTHENTICATED")

if __name__ == "__main__":
    unittest.main()
