"""
Measurement and Verification Accuracy Evaluation Benchmark.
Executes an independent test battery across multiple document categories,
with known ground truth labels (Authentic, Tampered/Forged, Unknown, Corrupted),
and measures empirical Accuracy, Precision, Recall, FPR, FNR, and Confusion Matrix.
"""
import os
import sys
import time

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import fitz as pymupdf
except ImportError:
    import pymupdf

from verification.engine import verification_engine


def create_pdf(path: str, lines: list, meta: dict = None):
    doc = pymupdf.open()
    page = doc.new_page()
    y = 50
    for line in lines:
        page.insert_text((50, y), line, fontsize=11)
        y += 22
    if meta:
        doc.set_metadata(meta)
    doc.save(path)
    doc.close()


def run_benchmark():
    eval_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "benchmark_eval_docs"))
    os.makedirs(eval_dir, exist_ok=True)

    # Labeled Evaluation Dataset Ground Truth:
    # label in {"AUTHENTICATED", "SUSPICIOUS", "NOT_VERIFIED", "VERIFICATION_FAILED"}
    test_cases = [
        # --- Authentic Documents ---
        {
            "filename": "eval_degree_auth.pdf",
            "lines": [
                "UNIVERSITY OF DELHI",
                "BACHELOR OF SCIENCE DEGREE CERTIFICATE",
                "This is to certify that Priya Nair has been admitted to the degree of Bachelor of Science.",
                "PRN: DU8921004 | Roll No: 190284",
                "Date of Issue: 20/06/2023",
                "Total Marks Obtained: 1350 / 1500 | Percentage: 90.00%",
                "Registrar",
                "Controller of Examinations"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Academic"
        },
        {
            "filename": "eval_hsc_auth.pdf",
            "lines": [
                "MAHARASHTRA STATE BOARD OF SECONDARY AND HIGHER SECONDARY EDUCATION",
                "STATEMENT OF MARKS - HIGHER SECONDARY CERTIFICATE EXAMINATION",
                "Candidate Name: Tanvi Patil",
                "Seat No: H209182",
                "Total Marks: 510 / 600 | Percentage: 85.00%",
                "Date: 25/05/2024"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Academic"
        },
        {
            "filename": "eval_pan_auth.pdf",
            "lines": [
                "INCOME TAX DEPARTMENT",
                "GOVT. OF INDIA",
                "PERMANENT ACCOUNT NUMBER",
                "ABCDE1234F",
                "Name: Rahul Sharma",
                "Father's Name: Vijay Sharma",
                "Date of Birth: 15/08/1998"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Identity"
        },
        {
            "filename": "eval_aadhaar_auth.pdf",
            "lines": [
                "UNIQUE IDENTIFICATION AUTHORITY OF INDIA",
                "GOVERNMENT OF INDIA",
                "Mera Aadhaar, Meri Pehchan",
                "XXXX XXXX 9988",
                "Name: Ananya Roy",
                "DOB: 12/03/2001",
                "Gender: Female"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Identity"
        },
        {
            "filename": "eval_invoice_auth.pdf",
            "lines": [
                "TAX INVOICE",
                "Invoice No: INV-8821",
                "Date: 10/05/2024",
                "Billed To: Global Systems Ltd",
                "GSTIN: 27ABCDE1234F1Z5",
                "Subtotal: Rs. 200000.00",
                "Tax Amount: Rs. 36000.00",
                "Total Amount: Rs. 236000.00",
                "Authorized Signatory"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Financial"
        },
        {
            "filename": "eval_salary_auth.pdf",
            "lines": [
                "TATA CONSULTANCY SERVICES",
                "PAYSLIP FOR THE MONTH OF SEPTEMBER 2024",
                "Employee Name: Siddharth Bose",
                "Employee ID: TCS-99881",
                "Designation: IT Analyst",
                "Basic Pay: 50000.00",
                "House Rent Allowance: 20000.00",
                "Total Deductions: 6000.00",
                "Net Pay: 64000.00"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Employment"
        },
        {
            "filename": "eval_cin_auth.pdf",
            "lines": [
                "MINISTRY OF CORPORATE AFFAIRS",
                "CERTIFICATE OF INCORPORATION",
                "Corporate Identity Number (CIN): U72200MH2021PTC123456",
                "Company Name: ALPHA ROBOTICS PRIVATE LIMITED",
                "Date of Incorporation: 14/01/2021",
                "Registrar of Companies, Pune"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Business"
        },
        {
            "filename": "eval_medical_auth.pdf",
            "lines": [
                "MEDICAL FITNESS CERTIFICATE",
                "This is to certify that Mr. Sameer Khan has been examined.",
                "He is physically fit to resume duties.",
                "Date: 04/09/2024",
                "Doctor Name: Dr. P. K. Sen, MBBS",
                "Registration No: MCI-19283"
            ],
            "expected_status": "AUTHENTICATED",
            "category": "Medical"
        },

        # --- Tampered / Suspicious Documents ---
        {
            "filename": "eval_marks_impossible.pdf",
            "lines": [
                "CENTRAL BOARD OF SECONDARY EDUCATION",
                "SENIOR SCHOOL CERTIFICATE EXAMINATION",
                "Candidate: Mohit Verma",
                "Seat No: 120938",
                "Total Marks Obtained: 560 / 500",  # Obtained > Maximum
                "Percentage: 112%"
            ],
            "expected_status": "SUSPICIOUS",
            "category": "Academic"
        },
        {
            "filename": "eval_pct_mismatch.pdf",
            "lines": [
                "STATE BOARD EXAMINATION",
                "STATEMENT OF MARKS",
                "Candidate: Alok Nath",
                "Roll No: 991823",
                "Total Marks Obtained: 400 / 500",  # Real is 80.00%
                "Percentage: 96.50%",  # Fabricated stated percentage
                "Date: 15/06/2024"
            ],
            "expected_status": "SUSPICIOUS",
            "category": "Academic"
        },
        {
            "filename": "eval_invoice_tampered.pdf",
            "lines": [
                "TAX INVOICE",
                "Invoice No: INV-9912",
                "GSTIN: 27ABCDE1234F1Z5",
                "Subtotal: Rs. 100000.00",
                "Tax Amount: Rs. 18000.00",
                "Total Amount: Rs. 165000.00"  # Inconsistent total
            ],
            "expected_status": "SUSPICIOUS",
            "category": "Financial"
        },
        {
            "filename": "eval_impossible_date.pdf",
            "lines": [
                "UNIVERSITY CERTIFICATE",
                "Candidate Name: Manish Gupta",
                "PRN: 99281002",
                "Date of Issue: 31/02/2024",  # Impossible calendar date
                "Controller of Examinations"
            ],
            "expected_status": "SUSPICIOUS",
            "category": "Academic"
        },
        {
            "filename": "eval_photoshop_tampered.pdf",
            "lines": [
                "SECONDARY SCHOOL EXAMINATION",
                "Candidate: Vikram Rao",
                "Roll No: 102938",
                "Date: 12/05/2023",
                "Marks: 450 / 500",
                "Percentage: 90.00%"
            ],
            "meta": {"producer": "Adobe Photoshop 2024 (Windows)", "creator": "Adobe Photoshop CC"},
            "expected_status": "SUSPICIOUS",
            "category": "Academic"
        },

        # --- Unknown Documents (Should return NOT_VERIFIED, never SUSPICIOUS) ---
        {
            "filename": "eval_recipe.pdf",
            "lines": [
                "Chocolate Chip Cookies Recipe",
                "1. Mix 2 cups flour and 1 cup sugar.",
                "2. Add 2 eggs and 1 stick butter.",
                "3. Fold in chocolate chips.",
                "4. Bake at 350F for 12 minutes."
            ],
            "expected_status": "NOT_VERIFIED",
            "category": "General"
        },
        {
            "filename": "eval_meeting_notes.pdf",
            "lines": [
                "Weekly Team Sync Notes",
                "Attendees: Dave, Sarah, Ken",
                "Discussion: Database migration planning",
                "Action item: Review SQL schema next Tuesday."
            ],
            "expected_status": "NOT_VERIFIED",
            "category": "General"
        },

        # --- Corrupted / Invalid Files ---
        {
            "filename": "eval_corrupted.pdf",
            "raw_bytes": b"NON_PDF_CORRUPTED_TRUNCATED_BYTES_HEX_0000",
            "expected_status": "VERIFICATION_FAILED",
            "category": "Corrupted"
        }
    ]

    print("=" * 70)
    print("DOCUMENT VERIFICATION BENCHMARK - EMPIRICAL ACCURACY EVALUATION")
    print("=" * 70)
    print(f"Total Evaluation Samples: {len(test_cases)}")
    print("Ground Truth Distribution:")
    gt_counts = {}
    for tc in test_cases:
        gt_counts[tc["expected_status"]] = gt_counts.get(tc["expected_status"], 0) + 1
    for st, cnt in gt_counts.items():
        print(f"  - {st:<22}: {cnt} samples")
    print("-" * 70)

    # Confusion matrix for binary forgery/suspicious detection:
    # Positive class = SUSPICIOUS / FORGED
    # Negative class = AUTHENTICATED / NOT_VERIFIED / FAILED
    tp = 0  # Actual Suspicious, Predicted Suspicious
    fp = 0  # Actual Not-Suspicious, Predicted Suspicious
    tn = 0  # Actual Not-Suspicious, Predicted Not-Suspicious
    fn = 0  # Actual Suspicious, Predicted Not-Suspicious

    correct_predictions = 0
    total_time = 0.0

    print(f"{'Filename':<28} | {'Category':<12} | {'Expected':<18} | {'Actual':<18} | {'Match'}")
    print("-" * 88)

    for tc in test_cases:
        fname = tc["filename"]
        fpath = os.path.join(eval_dir, fname)

        if "raw_bytes" in tc:
            with open(fpath, "wb") as f:
                f.write(tc["raw_bytes"])
        else:
            create_pdf(fpath, tc["lines"], tc.get("meta"))

        t0 = time.time()
        res = verification_engine.run_full_pipeline(fpath)
        elapsed = time.time() - t0
        total_time += elapsed

        actual_status = res["final_status"]
        expected_status = tc["expected_status"]
        matched = (actual_status == expected_status)
        if matched:
            correct_predictions += 1

        # Forgery detection binary metrics
        is_actual_suspicious = (expected_status == "SUSPICIOUS")
        is_pred_suspicious = (actual_status == "SUSPICIOUS")

        if is_actual_suspicious and is_pred_suspicious:
            tp += 1
        elif not is_actual_suspicious and is_pred_suspicious:
            fp += 1
        elif not is_actual_suspicious and not is_pred_suspicious:
            tn += 1
        elif is_actual_suspicious and not is_pred_suspicious:
            fn += 1

        mark = "[PASS]" if matched else "[FAIL]"
        print(f"{fname:<28} | {tc.get('category', 'N/A'):<12} | {expected_status:<18} | {actual_status:<18} | {mark}")

    print("=" * 70)
    print("EMPIRICAL PERFORMANCE METRICS")
    print("=" * 70)

    total_samples = len(test_cases)
    accuracy = (correct_predictions / total_samples) * 100.0
    precision = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
    fpr = (fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
    fnr = (fn / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0

    print(f"Overall Multi-Class Accuracy: {accuracy:.2f}% ({correct_predictions}/{total_samples})")
    print(f"Average Pipeline Latency   : {(total_time / total_samples) * 1000.0:.1f} ms / document")
    print("")
    print("Tampered/Forged Document Detection (Anomaly Classifier):")
    print(f"  - Precision               : {precision:.2f}%")
    print(f"  - Recall (Sensitivity)    : {recall:.2f}%")
    print(f"  - False Positive Rate(FPR): {fpr:.2f}% (Legitimate documents falsely flagged)")
    print(f"  - False Negative Rate(FNR): {fnr:.2f}% (Forged documents missed)")
    print("")
    print("Binary Confusion Matrix (Positive = SUSPICIOUS):")
    print(f"  True Positives  (TP) : {tp}")
    print(f"  False Positives (FP) : {fp}")
    print(f"  True Negatives  (TN) : {tn}")
    print(f"  False Negatives (FN) : {fn}")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
