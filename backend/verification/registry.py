"""
Universal Document Type Registry
Defines configurable document categories, canonical schemas, field requirements,
expected identifiers, and validation policies for all document types.
"""
from typing import Dict, Any, List, Optional


class DocumentTypeRegistry:
    """
    Central, extensible registry mapping document types across universal categories:
    Academic, Identity, Employment, Financial, Legal, Business, Medical, and General.
    Allows dynamic registration of new document types without modifying core engine logic.
    """

    _REGISTRY: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_type(
        cls,
        doc_type: str,
        category: str,
        required_fields: List[str],
        has_marks: bool = False,
        has_percentage: bool = False,
        has_financial_totals: bool = False,
        has_salary_breakdown: bool = False,
        has_qr: bool = False,
        has_barcode: bool = False,
        has_digital_signature: bool = False,
        issuing_bodies: Optional[List[str]] = None,
        expected_identifiers: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        description: str = ""
    ) -> None:
        """Registers or updates a document type profile in the registry."""
        cls._REGISTRY[doc_type] = {
            "name": doc_type,
            "category": category,
            "required_fields": required_fields,
            "has_marks": has_marks,
            "has_percentage": has_percentage,
            "has_financial_totals": has_financial_totals,
            "has_salary_breakdown": has_salary_breakdown,
            "has_qr": has_qr,
            "has_barcode": has_barcode,
            "has_digital_signature": has_digital_signature,
            "issuing_bodies": issuing_bodies or ["Official Authority"],
            "expected_identifiers": expected_identifiers or [],
            "keywords": keywords or [],
            "description": description or f"Universal document profile for {doc_type}"
        }

    @classmethod
    def get_profile(cls, doc_type: str) -> Dict[str, Any]:
        """Retrieves profile for a document type, falling back to a safe generic profile."""
        if not cls._REGISTRY:
            cls.initialize_defaults()
        return cls._REGISTRY.get(doc_type, {
            "name": doc_type or "Unknown Document",
            "category": "General",
            "required_fields": [],
            "has_marks": False,
            "has_percentage": False,
            "has_financial_totals": False,
            "has_salary_breakdown": False,
            "has_qr": False,
            "has_barcode": False,
            "has_digital_signature": False,
            "issuing_bodies": ["Official Authority"],
            "expected_identifiers": [],
            "keywords": [],
            "description": "Generic universal document profile"
        })

    @classmethod
    def get_category(cls, doc_type: str) -> str:
        """Returns the canonical category for a document type."""
        return cls.get_profile(doc_type).get("category", "General")

    @classmethod
    def list_all_types(cls) -> List[str]:
        """Lists all registered document types."""
        if not cls._REGISTRY:
            cls.initialize_defaults()
        return sorted(list(cls._REGISTRY.keys()))

    @classmethod
    def list_by_category(cls, category: str) -> List[str]:
        """Returns all document types registered under a specific category."""
        if not cls._REGISTRY:
            cls.initialize_defaults()
        return [k for k, v in cls._REGISTRY.items() if v.get("category", "").lower() == category.lower()]

    @classmethod
    def list_categories(cls) -> List[str]:
        """Returns all distinct categories registered."""
        if not cls._REGISTRY:
            cls.initialize_defaults()
        cats = {v.get("category", "General") for v in cls._REGISTRY.values()}
        return sorted(list(cats))

    @classmethod
    def initialize_defaults(cls) -> None:
        """Seeds the standard universal profiles covering all 8 major categories."""
        if cls._REGISTRY:
            return

        # -------------------------------------------------------------
        # 1. ACADEMIC CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "10th Marksheet",
            category="Academic",
            required_fields=["student_name", "seat_number", "examination_year"],
            has_marks=True,
            has_percentage=True,
            has_qr=True,
            issuing_bodies=["CBSE", "ICSE", "State Board", "MSBSHSE", "Secondary Education Board"],
            expected_identifiers=["seat_number", "roll_number", "certificate_number"],
            keywords=["secondary school", "class x", "10th", "ssc", "board of secondary education"]
        )
        cls.register_type(
            "12th Marksheet",
            category="Academic",
            required_fields=["student_name", "seat_number", "examination_year"],
            has_marks=True,
            has_percentage=True,
            has_qr=True,
            issuing_bodies=["CBSE", "CISCE", "State Board", "HSC Board", "Higher Secondary Board"],
            expected_identifiers=["seat_number", "roll_number", "certificate_number"],
            keywords=["higher secondary", "class xii", "12th", "hsc", "board of higher secondary education"]
        )
        cls.register_type(
            "Degree Certificate",
            category="Academic",
            required_fields=["student_name", "degree_title", "university_name"],
            has_marks=False,
            has_percentage=False,
            has_qr=True,
            issuing_bodies=["University", "Institute of Technology", "Autonomous College"],
            expected_identifiers=["prn_number", "registration_number", "convocation_number"],
            keywords=["degree of", "conferred upon", "bachelor of", "master of", "doctor of"]
        )
        cls.register_type(
            "Provisional Degree Certificate",
            category="Academic",
            required_fields=["student_name", "degree_title", "university_name"],
            has_marks=False,
            has_percentage=False,
            has_qr=True,
            issuing_bodies=["University", "Autonomous Institution"],
            expected_identifiers=["prn_number", "provisional_cert_no"],
            keywords=["provisional degree", "provisional certificate"]
        )
        cls.register_type(
            "Semester Marksheet",
            category="Academic",
            required_fields=["student_name", "semester", "seat_number"],
            has_marks=True,
            has_percentage=True,
            has_qr=True,
            issuing_bodies=["University", "College"],
            expected_identifiers=["seat_number", "prn_number", "roll_number"],
            keywords=["statement of marks", "semester", "sgpa", "cgpa", "grade card"]
        )
        cls.register_type(
            "Transcript",
            category="Academic",
            required_fields=["student_name", "institution_name"],
            has_marks=True,
            has_percentage=False,
            has_qr=False,
            issuing_bodies=["University", "College"],
            expected_identifiers=["transcript_number", "prn_number"],
            keywords=["official transcript", "academic transcript", "cumulative record"]
        )
        cls.register_type(
            "Bonafide Certificate",
            category="Academic",
            required_fields=["student_name", "institution_name", "issue_date"],
            has_marks=False,
            has_qr=False,
            issuing_bodies=["College", "School", "University"],
            expected_identifiers=["roll_number", "student_id"],
            keywords=["bonafide student", "bonafide certificate"]
        )
        cls.register_type(
            "Transfer Certificate",
            category="Academic",
            required_fields=["student_name", "institution_name", "issue_date"],
            has_marks=False,
            has_qr=False,
            issuing_bodies=["School", "College"],
            expected_identifiers=["tc_number", "admission_number"],
            keywords=["transfer certificate", "school leaving certificate", "college leaving"]
        )

        # -------------------------------------------------------------
        # 2. IDENTITY CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "PAN Card",
            category="Identity",
            required_fields=["identity_number", "name"],
            has_marks=False,
            has_qr=True,
            issuing_bodies=["Income Tax Department, Govt. of India"],
            expected_identifiers=["identity_number"],
            keywords=["permanent account number", "income tax department", "govt of india"]
        )
        cls.register_type(
            "Aadhaar Card",
            category="Identity",
            required_fields=["identity_number", "name"],
            has_marks=False,
            has_qr=True,
            issuing_bodies=["Unique Identification Authority of India (UIDAI)"],
            expected_identifiers=["identity_number"],
            keywords=["unique identification authority", "aadhaar", "uidai", "mera aadhaar"]
        )
        cls.register_type(
            "Voter ID",
            category="Identity",
            required_fields=["document_number", "name"],
            has_marks=False,
            has_qr=True,
            issuing_bodies=["Election Commission of India"],
            expected_identifiers=["document_number"],
            keywords=["election commission of india", "elector photo identity", "epic no"]
        )
        cls.register_type(
            "Passport",
            category="Identity",
            required_fields=["document_number", "name", "nationality", "dob"],
            has_marks=False,
            has_qr=False,
            issuing_bodies=["Ministry of External Affairs"],
            expected_identifiers=["document_number"],
            keywords=["republic of india", "passport", "type p", "country code ind"]
        )
        cls.register_type(
            "Driving Licence",
            category="Identity",
            required_fields=["document_number", "name", "valid_till"],
            has_marks=False,
            has_qr=True,
            issuing_bodies=["Ministry of Road Transport and Highways", "Regional Transport Office"],
            expected_identifiers=["document_number"],
            keywords=["driving licence", "union of india", "transport department", "dl no"]
        )

        # -------------------------------------------------------------
        # 3. EMPLOYMENT CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "Offer Letter",
            category="Employment",
            required_fields=["candidate_name", "company_name", "designation"],
            has_financial_totals=True,
            has_qr=False,
            has_digital_signature=True,
            issuing_bodies=["Employer", "Corporate Organization"],
            expected_identifiers=["reference_number", "candidate_id"],
            keywords=["offer letter", "we are pleased to offer", "compensation", "annual ctc"]
        )
        cls.register_type(
            "Appointment Letter",
            category="Employment",
            required_fields=["candidate_name", "company_name", "designation", "joining_date"],
            has_financial_totals=True,
            has_digital_signature=True,
            issuing_bodies=["Employer", "Corporate Organization"],
            expected_identifiers=["employee_id", "reference_number"],
            keywords=["letter of appointment", "terms of employment", "date of joining"]
        )
        cls.register_type(
            "Experience Certificate",
            category="Employment",
            required_fields=["employee_name", "company_name", "designation", "service_period"],
            has_digital_signature=True,
            issuing_bodies=["Employer", "Corporate Organization"],
            expected_identifiers=["employee_id", "reference_number"],
            keywords=["to whomsoever it may concern", "experience certificate", "relieving", "tenure of service"]
        )
        cls.register_type(
            "Salary Slip",
            category="Employment",
            required_fields=["employee_name", "net_pay", "month_year"],
            has_salary_breakdown=True,
            has_financial_totals=True,
            issuing_bodies=["Employer", "Corporate Organization"],
            expected_identifiers=["employee_id", "pan_number", "pf_number"],
            keywords=["payslip", "salary slip", "earnings", "deductions", "net pay", "basic salary"]
        )
        cls.register_type(
            "Relieving Letter",
            category="Employment",
            required_fields=["employee_name", "company_name", "relieving_date"],
            has_digital_signature=True,
            issuing_bodies=["Employer", "Corporate Organization"],
            expected_identifiers=["employee_id", "reference_number"],
            keywords=["relieving letter", "relieved from duties", "full and final settlement"]
        )

        # -------------------------------------------------------------
        # 4. FINANCIAL CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "Bank Statement",
            category="Financial",
            required_fields=["bank_name", "account_number", "statement_period"],
            has_financial_totals=True,
            issuing_bodies=["Scheduled Commercial Bank", "Reserve Bank of India"],
            expected_identifiers=["account_number", "ifsc_code"],
            keywords=["account statement", "transaction history", "balance", "debit", "credit", "ifsc"]
        )
        cls.register_type(
            "Invoice",
            category="Financial",
            required_fields=["invoice_number", "total_amount", "seller_name", "buyer_name"],
            has_financial_totals=True,
            has_qr=True,
            issuing_bodies=["Vendor", "Merchant", "Enterprise"],
            expected_identifiers=["invoice_number", "gstin"],
            keywords=["tax invoice", "bill of supply", "invoice no", "subtotal", "cgst", "sgst", "total amount"]
        )
        cls.register_type(
            "Fee Receipt",
            category="Financial",
            required_fields=["amount", "receipt_number", "payer_name"],
            has_financial_totals=True,
            issuing_bodies=["Educational Institution", "Organization"],
            expected_identifiers=["receipt_number", "student_id"],
            keywords=["fee receipt", "payment received", "tuition fee", "receipt no"]
        )
        cls.register_type(
            "Tax Return (ITR)",
            category="Financial",
            required_fields=["pan_number", "assessment_year", "total_income"],
            has_financial_totals=True,
            has_qr=True,
            issuing_bodies=["Income Tax Department, Govt. of India"],
            expected_identifiers=["pan_number", "ack_number"],
            keywords=["indian income tax return", "itr-v", "acknowledgement", "assessment year", "gross total income"]
        )
        cls.register_type(
            "Payment Receipt",
            category="Financial",
            required_fields=["receipt_number", "amount", "transaction_date"],
            has_financial_totals=True,
            issuing_bodies=["Bank", "Payment Gateway", "Merchant"],
            expected_identifiers=["transaction_id", "reference_number"],
            keywords=["payment receipt", "transaction successful", "amount paid", "payment reference"]
        )

        # -------------------------------------------------------------
        # 5. LEGAL CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "Affidavit",
            category="Legal",
            required_fields=["deponent_name", "declaration_text", "execution_date"],
            has_digital_signature=False,
            issuing_bodies=["Notary Public", "Oath Commissioner", "Judicial Magistrate"],
            expected_identifiers=["notary_reg_no", "stamp_number"],
            keywords=["affidavit", "solemnly affirm", "deponent", "verified at", "before me", "notary public"]
        )
        cls.register_type(
            "Agreement",
            category="Legal",
            required_fields=["party_one", "party_two", "agreement_date"],
            has_digital_signature=True,
            issuing_bodies=["Contracting Parties", "Legal Entity"],
            expected_identifiers=["agreement_number", "stamp_paper_no"],
            keywords=["this agreement", "between", "first party", "second party", "witnesseth", "in witness whereof"]
        )
        cls.register_type(
            "Declaration",
            category="Legal",
            required_fields=["declarant_name", "declaration_text", "date"],
            has_digital_signature=False,
            issuing_bodies=["Individual", "Authority"],
            expected_identifiers=["reference_number"],
            keywords=["self declaration", "hereby declare", "solemn affirmation", "true to the best of my knowledge"]
        )
        cls.register_type(
            "Contract",
            category="Legal",
            required_fields=["contract_parties", "effective_date"],
            has_digital_signature=True,
            issuing_bodies=["Corporate Entity", "Government Body"],
            expected_identifiers=["contract_id", "reference_number"],
            keywords=["service contract", "terms and conditions", "binding contract", "governing law"]
        )

        # -------------------------------------------------------------
        # 6. BUSINESS CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "Certificate of Incorporation",
            category="Business",
            required_fields=["company_name", "cin_number", "incorporation_date"],
            has_qr=True,
            has_digital_signature=True,
            issuing_bodies=["Registrar of Companies", "Ministry of Corporate Affairs"],
            expected_identifiers=["cin_number", "registration_number"],
            keywords=["ministry of corporate affairs", "certificate of incorporation", "companies act", "corporate identity number"]
        )
        cls.register_type(
            "GST Certificate",
            category="Business",
            required_fields=["legal_name", "document_number", "registration_date"],
            has_qr=True,
            issuing_bodies=["Goods and Services Tax Network", "Govt. of India"],
            expected_identifiers=["document_number"],
            keywords=["registration certificate", "goods and services tax", "gstin", "central goods and services"]
        )
        cls.register_type(
            "MSME/Udyam Certificate",
            category="Business",
            required_fields=["enterprise_name", "udyam_registration_number"],
            has_qr=True,
            issuing_bodies=["Ministry of Micro, Small and Medium Enterprises"],
            expected_identifiers=["udyam_registration_number"],
            keywords=["udyam registration certificate", "ministry of msme", "enterprise type", "udyam no"]
        )
        cls.register_type(
            "Purchase Order",
            category="Business",
            required_fields=["po_number", "vendor_name", "total_amount"],
            has_financial_totals=True,
            issuing_bodies=["Purchasing Entity", "Company"],
            expected_identifiers=["po_number", "vendor_id"],
            keywords=["purchase order", "po no", "vendor", "deliver to", "item description", "quantity"]
        )

        # -------------------------------------------------------------
        # 7. MEDICAL CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "Medical Fitness Certificate",
            category="Medical",
            required_fields=["patient_name", "doctor_name", "medical_reg_no", "examination_date"],
            has_digital_signature=True,
            issuing_bodies=["Registered Medical Practitioner", "Hospital", "Health Authority"],
            expected_identifiers=["medical_reg_no", "certificate_number"],
            keywords=["medical fitness", "physically fit", "registered medical practitioner", "doctor signature"]
        )
        cls.register_type(
            "Prescription",
            category="Medical",
            required_fields=["patient_name", "doctor_name", "prescription_date"],
            issuing_bodies=["Clinic", "Hospital", "Physician"],
            expected_identifiers=["medical_reg_no", "rx_number"],
            keywords=["rx", "prescription", "dosage", "diagnosis", "clinic", "hospital"]
        )
        cls.register_type(
            "Laboratory Report",
            category="Medical",
            required_fields=["patient_name", "test_name", "report_date"],
            issuing_bodies=["Diagnostic Laboratory", "Pathology Lab"],
            expected_identifiers=["sample_id", "lab_ref_no"],
            keywords=["diagnostic laboratory", "pathology report", "reference range", "specimen", "test result"]
        )
        cls.register_type(
            "Discharge Summary",
            category="Medical",
            required_fields=["patient_name", "admission_date", "discharge_date", "hospital_name"],
            issuing_bodies=["Hospital", "Medical Center"],
            expected_identifiers=["ipd_number", "uhid"],
            keywords=["discharge summary", "date of admission", "date of discharge", "condition at discharge"]
        )

        # -------------------------------------------------------------
        # 8. GENERAL / GOVERNMENT CATEGORY
        # -------------------------------------------------------------
        cls.register_type(
            "7/12 Extract",
            category="Property",
            required_fields=["gat_or_survey", "village", "taluka", "district"],
            has_qr=True,
            issuing_bodies=["Revenue Department, Govt. of Maharashtra"],
            expected_identifiers=["gat_number", "survey_number", "khata_number"],
            keywords=["gaon namuna saat", "7/12", "adhikar abhilekh", "bhogwata", "survey no"]
        )
        cls.register_type(
            "Caste Certificate",
            category="Government",
            required_fields=["candidate_name", "caste_category", "issuing_authority"],
            has_qr=True,
            issuing_bodies=["Office of the Tahasildar / SDO", "Competent Authority"],
            expected_identifiers=["certificate_number", "application_number"],
            keywords=["caste certificate", "scheduled caste", "other backward class", "competent authority"]
        )
        cls.register_type(
            "Income Certificate",
            category="Government",
            required_fields=["candidate_name", "annual_income", "issuing_authority"],
            has_financial_totals=True,
            has_qr=True,
            issuing_bodies=["Office of the Tahasildar / Revenue Department"],
            expected_identifiers=["certificate_number", "barcode"],
            keywords=["income certificate", "annual income", "tahasildar", "revenue department"]
        )
        cls.register_type(
            "Domicile Certificate",
            category="Government",
            required_fields=["candidate_name", "residence_period", "issuing_authority"],
            has_qr=True,
            issuing_bodies=["Office of the Sub-Divisional Officer / Tahasildar"],
            expected_identifiers=["certificate_number"],
            keywords=["domicile certificate", "age and nationality", "resident of"]
        )
        cls.register_type(
            "General Document",
            category="General",
            required_fields=[],
            issuing_bodies=["Official Authority"],
            expected_identifiers=[],
            keywords=[],
            description="Unstructured or general purpose document"
        )


# Pre-seed registry on load
DocumentTypeRegistry.initialize_defaults()
