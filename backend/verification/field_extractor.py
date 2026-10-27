"""
Universal Field Extraction Service
Extracts category-specific structured fields, identifiers, dates, financial amounts,
and entities from normalized OCR text across all document types.
"""
import re
from typing import Dict, Any, Optional
from utils.document_utils import mask_sensitive_data


class FieldExtractionService:
    """
    Modular, category-aware field extractor supporting Academic, Identity, Employment,
    Financial, Legal, Business, Medical, and General document schemas.
    """

    @classmethod
    def extract_fields(cls, text: str, doc_type: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts structured fields matching the document category and type.
        """
        data: Dict[str, Any] = {
            # Common metadata fields
            "name": None,
            "holder_name": None,
            "student_name": None,
            "employee_name": None,
            "patient_name": None,
            "deponent_name": None,
            "father_name": None,
            "dob": None,
            "date_of_birth": None,
            "date": None,
            "issue_date": None,
            "expiry_date": None,
            "institute_name": None,
            "company_name": None,
            "bank_name": None,
            "hospital_name": None,

            # Identifiers
            "identity_number": None,
            "prn_number": None,
            "seat_number": None,
            "roll_number": None,
            "registration_number": None,
            "certificate_number": None,
            "document_number": None,
            "account_number": None,
            "ifsc_code": None,
            "invoice_number": None,
            "receipt_number": None,
            "employee_id": None,
            "cin_number": None,
            "gstin": None,
            "udyam_registration_number": None,
            "medical_reg_no": None,

            # Academic specific
            "marks_obtained": None,
            "maximum_marks": None,
            "total_marks": None,
            "percentage": None,
            "cgpa": None,
            "sgpa": None,
            "result_status": None,
            "examination_year": None,
            "semester": None,
            "degree_title": None,

            # Financial specific
            "subtotal": None,
            "tax_amount": None,
            "total_amount": None,
            "balance": None,
            "amount": None,

            # Employment specific
            "designation": None,
            "joining_date": None,
            "relieving_date": None,
            "basic_salary": None,
            "hra": None,
            "allowances": None,
            "deductions": None,
            "net_pay": None,
            "pf_number": None,

            # Legal specific
            "party_one": None,
            "party_two": None,
            "notary_reg_no": None,
            "stamp_number": None,

            # Medical specific
            "doctor_name": None,
            "diagnosis": None
        }

        if not text:
            return data

        # 1. Names Extraction
        cls._extract_names(text, data)

        # 2. Date Parsing
        cls._extract_dates(text, data)

        # 3. Universal Identifiers
        cls._extract_identifiers(text, data)

        # 4. Academic Numbers & Percentages
        cls._extract_academic(text, data)

        # 5. Financial Figures (Totals, Subtotals, Taxes)
        cls._extract_financial(text, data)

        # 6. Employment & Salary Figures
        cls._extract_employment(text, data)

        # 7. Business & Organization Entities
        cls._extract_business(text, data)

        # 8. Legal & Medical Entities
        cls._extract_legal_and_medical(text, data)

        # Unify generic aliases
        primary_name = (
            data["student_name"] or
            data["employee_name"] or
            data["patient_name"] or
            data["deponent_name"] or
            data["holder_name"] or
            data["name"]
        )
        data["name"] = primary_name
        data["holder_name"] = primary_name

        return data

    @classmethod
    def _extract_names(cls, text: str, data: Dict[str, Any]) -> None:
        name_patterns = [
            r"(?:certify\s+that|conferred\s+upon|awarded\s+to|presented\s+to|certified\s+that,?\s*(?:kumar|kumari|shri|smt)?)\s+([A-Z][A-Za-z\s]{2,40})(?:\s+has|\s+having|\s+son|\s+daughter|\s+of|\s+bearing|\s+r\/o)",
            r"(?:candidate(?:'s)?\s*name|student(?:'s)?\s*name|name\s*of\s*(?:the\s*)?candidate|name\s*of\s*(?:the\s*)?student|holder(?:'s)?\s*name)[:.\s]+([A-Za-z\s]{3,40})",
            r"(?:employee\s*name|name\s*of\s*employee)[:.\s]+([A-Za-z\s]{3,40})",
            r"(?:patient\s*name|name\s*of\s*patient)[:.\s]+([A-Za-z\s]{3,40})",
            r"(?:deponent|declarant|first\s*party|party\s*one)[:.\s]+([A-Za-z\s]{3,40})",
            r"(?:elector(?:'s)?\s*name|name)[:.\s]+([A-Za-z\s]{3,40})"
        ]
        excluded = ['marksheet', 'certificate', 'university', 'board', 'examination', 'statement', 'submission', 'proofs', 'document', 'invoice', 'statement', 'signature', 'date', 'total']

        for pat in name_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().split('\n')[0]
                if len(cand) > 2 and not any(w in cand.lower() for w in excluded):
                    data["student_name"] = cand
                    data["holder_name"] = cand
                    break

        father_match = re.search(r"(?:father(?:'s)?\s*name|parent(?:'s)?\s*name|s\/o|d\/o|w\/o)[:.\s]+([A-Za-z\s]{3,40})", text, re.IGNORECASE)
        if father_match:
            f_cand = father_match.group(1).strip().split('\n')[0]
            if len(f_cand) > 2 and not any(w in f_cand.lower() for w in excluded):
                data["father_name"] = f_cand

    @classmethod
    def _extract_dates(cls, text: str, data: Dict[str, Any]) -> None:
        dob_match = re.search(r'(?:date\s*of\s*birth|dob|birth\s*date)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
        if dob_match:
            data["dob"] = dob_match.group(1).strip()
            data["date_of_birth"] = data["dob"]

        issue_match = re.search(r'(?:date\s+of\s+issue|issue\s+date|issued\s+on|date\s*:\s*)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
        if issue_match:
            data["issue_date"] = issue_match.group(1).strip()
            data["date"] = data["issue_date"]

        expiry_match = re.search(r'(?:valid\s+till|valid\s+upto|expiry\s+date|validity)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
        if expiry_match:
            data["expiry_date"] = expiry_match.group(1).strip()

        joining_match = re.search(r'(?:date\s+of\s+joining|joining\s+date|effective\s+date)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
        if joining_match:
            data["joining_date"] = joining_match.group(1).strip()

        relieving_match = re.search(r'(?:date\s+of\s+relieving|relieving\s+date)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
        if relieving_match:
            data["relieving_date"] = relieving_match.group(1).strip()

    @classmethod
    def _extract_identifiers(cls, text: str, data: Dict[str, Any]) -> None:
        # Aadhaar
        aadhaar_match = re.search(r'\b(?:\d{4}|[Xx]{4})[\s\-](?:\d{4}|[Xx]{4})[\s\-](\d{4})\b', text)
        if aadhaar_match:
            data["identity_number"] = f"XXXX XXXX {aadhaar_match.group(1)}"

        # PAN
        pan_match = re.search(r'\b([A-Z]{5}\d{4}[A-Z])\b', text)
        if pan_match:
            data["identity_number"] = pan_match.group(1)

        # Voter ID (EPIC)
        epic_match = re.search(r'\b([A-Z]{3}\d{7})\b', text)
        if epic_match:
            data["identity_number"] = epic_match.group(1)
            data["document_number"] = epic_match.group(1)

        # Passport
        passport_match = re.search(r'\b([A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9])\b', text)
        if passport_match:
            data["document_number"] = passport_match.group(1).replace(" ", "")

        # Driving Licence
        dl_match = re.search(r'\b([A-Z]{2}[-\s]?\d{2}[-\s]?[12]\d{3}[-\s]?\d{7})\b', text)
        if dl_match:
            data["document_number"] = dl_match.group(1)

        # Academic PRN / Seat
        prn_match = re.search(r'(?:p\.?r\.?n\.?(?:\s*no\.?)?|permanent\s*registration\s*no\.?)[:.\s]*([A-Z0-9\-]{5,20})', text, re.IGNORECASE)
        if prn_match:
            data["prn_number"] = prn_match.group(1).strip()

        seat_match = re.search(r'(?:seat\s*(?:no|number)|seat\s*no\.?)[:.\s]*([A-Z0-9\-\/]{3,20})', text, re.IGNORECASE)
        if seat_match:
            data["seat_number"] = seat_match.group(1).strip()

        roll_match = re.search(r'(?:roll\s*(?:no|number)|reg(?:istration)?\s*(?:no|number)|enrollment\s*no)[:.\s]*([A-Z0-9\-\/]{3,24})', text, re.IGNORECASE)
        if roll_match:
            val = roll_match.group(1).strip()
            data["roll_number"] = val
            data["registration_number"] = val

        cert_match = re.search(r'(?:cert(?:ificate)?\s*(?:no|number)|serial\s*(?:no|number)|sl\.?\s*no\.?|sr\.?\s*no\.?)[:.\s]*([A-Z0-9\-\/]{3,24})', text, re.IGNORECASE)
        if cert_match:
            data["certificate_number"] = cert_match.group(1).strip()

        # Bank Account & IFSC
        acc_match = re.search(r'(?:account\s*(?:no|number)|a\/c\s*no\.?)[:.\s]*([0-9]{9,18})', text, re.IGNORECASE)
        if acc_match:
            data["account_number"] = acc_match.group(1).strip()

        ifsc_match = re.search(r'\b([A-Z]{4}0[A-Z0-9]{6})\b', text)
        if ifsc_match:
            data["ifsc_code"] = ifsc_match.group(1)

        # Invoice & Receipt Number
        inv_match = re.search(r'(?:invoice\s*(?:no|number)|bill\s*no\.?)[:.\s]*([A-Za-z0-9\-\/]{3,24})', text, re.IGNORECASE)
        if inv_match:
            data["invoice_number"] = inv_match.group(1).strip()

        rec_match = re.search(r'(?:receipt\s*(?:no|number))[:.\s]*([A-Za-z0-9\-\/]{3,24})', text, re.IGNORECASE)
        if rec_match:
            data["receipt_number"] = rec_match.group(1).strip()

        # Corporate CIN & GSTIN
        cin_match = re.search(r'\b([UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})\b', text)
        if cin_match:
            data["cin_number"] = cin_match.group(1)

        gstin_match = re.search(r'\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1})\b', text)
        if gstin_match:
            data["gstin"] = gstin_match.group(1)

        udyam_match = re.search(r'\b(UDYAM-[A-Z]{2}-\d{2}-\d{7})\b', text, re.IGNORECASE)
        if udyam_match:
            data["udyam_registration_number"] = udyam_match.group(1).upper()

    @classmethod
    def _extract_academic(cls, text: str, data: Dict[str, Any]) -> None:
        clean_for_marks = re.sub(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b', ' ', text)
        clean_for_marks = re.sub(r'(?:no\.?|ref(?:erence)?\.?|g\.?r\.?|case|order|reg(?:istration)?)\s*[:.\s]*[A-Za-z0-9\-]*\d+[\/\\]\d+[A-Za-z0-9\-]*', ' ', clean_for_marks, flags=re.IGNORECASE)

        marks_match = re.search(r'(?:total\s*marks(?:\s*obtained)?|grand\s*total|marks\s*obtained|total\s*score)[:.\s]*(\d{2,4})\s*(?:[\/\\]|\s+out\s+of\s+)\s*(\d{2,4})', clean_for_marks, re.IGNORECASE)
        if not marks_match:
            marks_match = re.search(r'\b(?:marks|total|score)\s*[:.\s]+(\d{2,4})\s*(?:[\/\\]|\s+out\s+of\s+)\s*(\d{2,4})\b', clean_for_marks, re.IGNORECASE)

        if marks_match:
            try:
                obt = float(marks_match.group(1))
                mx = float(marks_match.group(2))
                data["marks_obtained"] = obt
                data["maximum_marks"] = mx
                data["total_marks"] = mx
            except ValueError:
                pass

        pct_match = re.search(r'(\d{1,3}(?:\.\d{1,2})?)\s*%', text)
        if pct_match:
            data["percentage"] = pct_match.group(1).strip() + "%"

        cgpa_match = re.search(r'(?:cgpa|sgpa|gpa|grade\s*point\s*average)[:.\s]*(\d{1,2}(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if cgpa_match:
            try:
                cgpa_val = float(cgpa_match.group(1))
                data["cgpa"] = cgpa_val
                data["sgpa"] = cgpa_val
            except ValueError:
                pass

    @classmethod
    def _extract_financial(cls, text: str, data: Dict[str, Any]) -> None:
        # Subtotal
        sub_match = re.search(r'(?:sub\s*total|subtotal|taxable\s*value)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if sub_match:
            try:
                data["subtotal"] = float(sub_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Tax
        tax_match = re.search(r'(?:total\s*tax|tax\s*amount|gst\s*amount|vat\s*amount)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if tax_match:
            try:
                data["tax_amount"] = float(tax_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Grand Total / Total Amount (exclude subtotal)
        tot_match = re.search(r'(?<!sub)(?<!sub\s)\b(?:grand\s*total|total\s*amount|invoice\s*total|net\s*amount|amount\s*payable|total)\b[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if tot_match:
            try:
                val = float(tot_match.group(1).replace(",", ""))
                data["total_amount"] = val
                data["amount"] = val
            except ValueError:
                pass

        # Account Balance
        bal_match = re.search(r'(?:available\s*balance|closing\s*balance|net\s*balance)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if bal_match:
            try:
                data["balance"] = float(bal_match.group(1).replace(",", ""))
            except ValueError:
                pass

    @classmethod
    def _extract_employment(cls, text: str, data: Dict[str, Any]) -> None:
        # Designation
        desig_match = re.search(r'(?:designation|position|job\s*title)[:.\s]+([A-Za-z\s]{3,40})', text, re.IGNORECASE)
        if desig_match:
            data["designation"] = desig_match.group(1).strip().split('\n')[0]

        # Net Pay / Net Salary
        net_match = re.search(r'(?:net\s*pay|net\s*salary|take\s*home)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if net_match:
            try:
                data["net_pay"] = float(net_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Basic Salary
        basic_match = re.search(r'(?:basic\s*(?:pay|salary)?|basic)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if basic_match:
            try:
                data["basic_salary"] = float(basic_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # HRA
        hra_match = re.search(r'(?:h\.?r\.?a\.?|house\s*rent\s*allowance)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if hra_match:
            try:
                data["hra"] = float(hra_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # Deductions
        ded_match = re.search(r'(?:total\s*deductions?|deductions?)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if ded_match:
            try:
                data["deductions"] = float(ded_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # PF Number
        pf_match = re.search(r'(?:pf\s*(?:no|number)|provident\s*fund\s*no\.?)[:.\s]*([A-Z0-9\/]{6,26})', text, re.IGNORECASE)
        if pf_match:
            data["pf_number"] = pf_match.group(1).strip()

        # Employee ID
        emp_id_match = re.search(r'(?:employee\s*(?:id|code|number)|emp\s*id)[:.\s]*([A-Za-z0-9\-]{3,16})', text, re.IGNORECASE)
        if emp_id_match:
            data["employee_id"] = emp_id_match.group(1).strip()

    @classmethod
    def _extract_business(cls, text: str, data: Dict[str, Any]) -> None:
        comp_match = re.search(r'(?:company\s*name|name\s*of\s*the\s*company|organization)[:.\s]+([A-Za-z0-9\s.,&]{3,50}(?:pvt\.?\s*ltd\.?|limited|corp|inc|llp)?)', text, re.IGNORECASE)
        if comp_match:
            cand = comp_match.group(1).strip().split('\n')[0]
            if len(cand) > 3:
                data["company_name"] = cand

        bank_match = re.search(r'(?:bank\s*name|name\s*of\s*bank)[:.\s]+([A-Za-z\s]{3,40}(?:bank)?)', text, re.IGNORECASE)
        if bank_match:
            data["bank_name"] = bank_match.group(1).strip().split('\n')[0]

    @classmethod
    def _extract_legal_and_medical(cls, text: str, data: Dict[str, Any]) -> None:
        notary_match = re.search(r'(?:notary\s*reg(?:istration)?\s*(?:no|number)|advocate\s*reg\s*no\.?)[:.\s]*([A-Za-z0-9\-\/]{4,20})', text, re.IGNORECASE)
        if notary_match:
            data["notary_reg_no"] = notary_match.group(1).strip()

        doc_reg_match = re.search(r'(?:dr\.?|doctor|physician)?\s*(?:reg(?:istration)?\s*(?:no|number)|mci\s*reg\s*no\.?)[:.\s]*([A-Za-z0-9\-\/]{4,20})', text, re.IGNORECASE)
        if doc_reg_match:
            data["medical_reg_no"] = doc_reg_match.group(1).strip()

        diag_match = re.search(r'(?:diagnosis|clinical\s*impression|suffering\s*from)[:.\s]+([A-Za-z0-9\s.,-]{3,60})', text, re.IGNORECASE)
        if diag_match:
            data["diagnosis"] = diag_match.group(1).strip().split('\n')[0]
