import os
import sys
import unittest

try:
    import fitz as pymupdf
except ImportError:
    try:
        import pymupdf
    except ImportError:
        pymupdf = None

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.engine import verification_engine
from verification.registry import DocumentTypeRegistry
from verification.field_extractor import FieldExtractionService


class TestUniversalVerificationSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "universal_test_docs"))
        os.makedirs(cls.scratch_dir, exist_ok=True)

    def create_pdf(self, filename: str, text_lines: list, meta: dict = None) -> str:
        path = os.path.join(self.scratch_dir, filename)
        doc = pymupdf.open()
        page = doc.new_page()
        y = 50
        for line in text_lines:
            page.insert_text((50, y), line, fontsize=11)
            y += 22
        if meta:
            doc.set_metadata(meta)
        doc.save(path)
        doc.close()
        return path

    def test_01_registry_coverage_all_categories(self):
        """Verify that DocumentTypeRegistry covers all required 8 major categories"""
        categories = DocumentTypeRegistry.list_categories()
        expected = ["Academic", "Business", "Employment", "Financial", "General", "Identity", "Legal", "Medical"]
        for exp in expected:
            self.assertIn(exp, categories, f"Category '{exp}' should be registered in DocumentTypeRegistry")

    def test_02_invoice_financial_totals_passed(self):
        """Test valid commercial Tax Invoice with correct arithmetic (Subtotal + Tax == Total)"""
        pdf = self.create_pdf(
            "valid_invoice.pdf",
            [
                "TAX INVOICE",
                "Invoice No: INV-2024-9988",
                "Date: 12/04/2024",
                "Seller: TechCorp Solutions Pvt Ltd",
                "GSTIN: 27ABCDE1234F1Z5",
                "Billed To: Apex Enterprises",
                "Item: Software Development Services",
                "Subtotal: Rs. 100000.00",
                "Tax Amount: Rs. 18000.00",
                "Total Amount: Rs. 118000.00",
                "Authorized Signatory"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["category"], "Financial")
        self.assertEqual(res["doc_type_detected"], "Invoice")
        self.assertEqual(res["checks"]["field_consistency"], "PASSED")
        self.assertGreaterEqual(res["classification_confidence"], 80.0)

    def test_03_invoice_financial_totals_suspicious(self):
        """Test altered Tax Invoice with arithmetic mismatch (Subtotal 100k + Tax 18k != Total 150k)"""
        pdf = self.create_pdf(
            "altered_invoice.pdf",
            [
                "TAX INVOICE",
                "Invoice No: INV-2024-9989",
                "Date: 12/04/2024",
                "Seller: TechCorp Solutions Pvt Ltd",
                "GSTIN: 27ABCDE1234F1Z5",
                "Subtotal: Rs. 100000.00",
                "Tax Amount: Rs. 18000.00",
                "Total Amount: Rs. 150000.00",  # Fraudulent total
                "Authorized Signatory"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_04_salary_slip_employment_passed(self):
        """Test valid Salary Slip with consistent earnings and deductions"""
        pdf = self.create_pdf(
            "salary_slip_valid.pdf",
            [
                "INFOSYS TECHNOLOGIES LIMITED",
                "PAYSLIP FOR THE MONTH OF OCTOBER 2024",
                "Employee Name: Rohan Kulkarni",
                "Employee ID: EMP-50921",
                "Designation: Senior Systems Engineer",
                "PAN: ABCPK1234D",
                "PF Number: MH/PUN/0012345/000/123",
                "Basic Pay: 40000.00",
                "House Rent Allowance: 15000.00",
                "Total Deductions: 5000.00",
                "Net Pay: 50000.00",  # 40000 + 15000 - 5000 = 50000
                "Bank Account No: 123456789012"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["category"], "Employment")
        self.assertEqual(res["doc_type_detected"], "Salary Slip")
        self.assertEqual(res["checks"]["field_consistency"], "PASSED")

    def test_05_salary_slip_discrepancy_suspicious(self):
        """Test Salary Slip with arithmetic tampering in Net Pay"""
        pdf = self.create_pdf(
            "salary_slip_forged.pdf",
            [
                "INFOSYS TECHNOLOGIES LIMITED",
                "PAYSLIP FOR THE MONTH OF OCTOBER 2024",
                "Employee Name: Rohan Kulkarni",
                "Employee ID: EMP-50921",
                "Basic Pay: 40000.00",
                "House Rent Allowance: 15000.00",
                "Total Deductions: 5000.00",
                "Net Pay: 75000.00",  # Mathematically inconsistent
                "Bank Account No: 123456789012"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "SUSPICIOUS")
        self.assertEqual(res["checks"]["field_consistency"], "SUSPICIOUS")

    def test_06_business_incorporation_cin_validation(self):
        """Test Certificate of Incorporation with valid Ministry of Corporate Affairs CIN"""
        pdf = self.create_pdf(
            "cert_incorporation.pdf",
            [
                "MINISTRY OF CORPORATE AFFAIRS",
                "GOVERNMENT OF INDIA",
                "CERTIFICATE OF INCORPORATION",
                "[Pursuant to sub-section (2) of section 7 of the Companies Act, 2013]",
                "I hereby certify that NEXTGEN INNOVATIONS PRIVATE LIMITED is incorporated on this day.",
                "Corporate Identity Number (CIN): U72200MH2022PTC384920",
                "Date of Incorporation: 18/02/2022",
                "Registrar of Companies, Mumbai"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["category"], "Business")
        self.assertEqual(res["doc_type_detected"], "Certificate of Incorporation")
        self.assertEqual(res["checks"]["identifier_validation"], "PASSED")

    def test_07_medical_fitness_certificate_passed(self):
        """Test standard Medical Fitness Certificate"""
        pdf = self.create_pdf(
            "medical_cert.pdf",
            [
                "MEDICAL FITNESS CERTIFICATE",
                "This is to certify that I have examined Mr. Suresh Desai.",
                "He is in good mental and bodily health and free from any physical defect.",
                "He is physically fit to resume academic and sports activities.",
                "Date of Examination: 10/08/2024",
                "Doctor Name: Dr. A. V. Rao, MBBS, MD",
                "Medical Council Registration No: MCI-782910"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["category"], "Medical")
        self.assertIn("Medical", res["doc_type_detected"])

    def test_08_legal_affidavit_passed(self):
        """Test legal Affidavit executed before Notary Public"""
        pdf = self.create_pdf(
            "legal_affidavit.pdf",
            [
                "BEFORE THE NOTARY PUBLIC, PUNE",
                "AFFIDAVIT",
                "I, Ramesh Chandra Joshi, aged 45 years, residing at Pune, do hereby solemnly affirm and state on oath as follows:",
                "1. That all statements made herein are true to the best of my knowledge.",
                "2. That I have not suppressed any material information.",
                "Verified and signed at Pune on this 14th day of March 2024.",
                "Deponent: Ramesh Chandra Joshi",
                "Sworn before me: Notary Advocate, Govt. of Maharashtra",
                "Notary Reg No: NOT-PUN-4091"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "AUTHENTICATED")
        self.assertEqual(res["category"], "Legal")
        self.assertEqual(res["doc_type_detected"], "Affidavit")

    def test_09_unknown_document_safe_guardrail(self):
        """Test non-supported document (e.g., Recipe or Grocery List) returning NOT_VERIFIED (never SUSPICIOUS)"""
        pdf = self.create_pdf(
            "grocery_list.pdf",
            [
                "Weekly Shopping List",
                "- Tomatoes 2 kg",
                "- Onions 3 kg",
                "- Olive oil 1 bottle",
                "- Pasta 500g",
                "- Parmesan cheese"
            ]
        )
        res = verification_engine.run_full_pipeline(pdf)
        self.assertEqual(res["final_status"], "NOT_VERIFIED")
        self.assertEqual(res["doc_type_detected"], "Unknown Document")
        self.assertEqual(res["classification_status"], "UNKNOWN_DOCUMENT")
        self.assertLess(res["classification_confidence"], 40.0)

    def test_10_field_extractor_universal_schemas(self):
        """Test that FieldExtractionService correctly parses amounts, identifiers, and entities"""
        text = (
            "TAX INVOICE\n"
            "Invoice No: INV-4455\n"
            "Billed To: Vikram Mehta\n"
            "GSTIN: 27AABCS1429B1Z1\n"
            "Subtotal: Rs. 50,000.00\n"
            "Tax Amount: Rs. 9,000.00\n"
            "Total Amount: Rs. 59,000.00\n"
            "Date of Issue: 20/09/2024\n"
        )
        extracted = FieldExtractionService.extract_fields(text, doc_type="Invoice", category="Financial")
        self.assertEqual(extracted["invoice_number"], "INV-4455")
        self.assertEqual(extracted["gstin"], "27AABCS1429B1Z1")
        self.assertEqual(extracted["subtotal"], 50000.0)
        self.assertEqual(extracted["tax_amount"], 9000.0)
        self.assertEqual(extracted["total_amount"], 59000.0)
        self.assertEqual(extracted["issue_date"], "20/09/2024")


if __name__ == "__main__":
    unittest.main()
