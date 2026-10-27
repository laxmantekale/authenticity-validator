import logging
from typing import Dict, Any, Tuple

from verification.rule_engine.classification_rules import ClassificationRules
from verification.rule_engine.document_rules import DocumentRules
from verification.rule_engine.field_rules import FieldRules
from verification.rule_engine.identifier_rules import IdentifierRules
from verification.rule_engine.issuer_rules import IssuerRules
from verification.rule_engine.date_rules import DateRules
from verification.rule_engine.qr_rules import QRRules
from verification.rule_engine.barcode_rules import BarcodeRules
from verification.rule_engine.signature_rules import SignatureRules
from verification.rule_engine.metadata_rules import MetadataRules

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Centralized Rule Engine combining all deterministic, evidence-based verification rules.
    """

    def __init__(self):
        self.classification_rules = ClassificationRules
        self.document_rules = DocumentRules
        self.field_rules = FieldRules
        self.identifier_rules = IdentifierRules
        self.issuer_rules = IssuerRules
        self.date_rules = DateRules
        self.qr_rules = QRRules
        self.barcode_rules = BarcodeRules
        self.signature_rules = SignatureRules
        self.metadata_rules = MetadataRules

    def execute_rules(
        self,
        file_path: str,
        ocr_text: str,
        extracted_fields: Dict[str, Any],
        user_selected_type: str = None
    ) -> Dict[str, Any]:
        """
        Executes the complete rule-based validation pipeline.
        Returns a comprehensive dictionary with individual rule outputs and aggregate findings.
        """
        # 1. Automatic Document Identification
        doc_type, category, classification_conf, class_details = self.classification_rules.identify_document(
            ocr_text=ocr_text,
            file_path=file_path
        )

        is_unknown = (doc_type == "Unknown Document")
        profile = self.document_rules.get_profile(doc_type)

        # 2. Field & Numerical Validation
        marks_res = self.field_rules.validate_marks_and_percentage(extracted_fields, raw_text=ocr_text, doc_type=doc_type)
        req_res = self.field_rules.validate_required_fields_present(doc_type, extracted_fields, raw_text=ocr_text)

        # 3. Identifier Structure Validation
        id_res = self.identifier_rules.validate_document_identifiers(doc_type, extracted_fields)

        # 4. Issuer Validation
        issuer_res = self.issuer_rules.identify_and_validate_issuer(doc_type, ocr_text)

        # 5. Date & Chronological Validation
        date_res = self.date_rules.validate_date_consistency(extracted_fields, raw_text=ocr_text)

        # 6. QR Code Detection & Validation
        qr_res = self.qr_rules.verify_qr(file_path, ocr_text=ocr_text)

        # 7. Barcode Detection & Validation
        barcode_res = self.barcode_rules.verify_barcode(file_path, ocr_text=ocr_text)

        # 8. Digital Signature & Signatory Designation
        digital_sig_res = self.signature_rules.check_pdf_digital_signature(file_path)
        signatory_res = self.signature_rules.check_signatory_block(ocr_text)

        # 9. Metadata & Software Manipulation Analysis
        metadata_res = self.metadata_rules.analyze_metadata(file_path)

        # Compile Rule Suite Report
        return {
            "document_type": doc_type,
            "category": category,
            "classification_confidence": classification_conf,
            "classification_status": "SUPPORTED_DOCUMENT" if not is_unknown else "UNKNOWN_DOCUMENT",
            "is_unknown": is_unknown,
            "profile": profile,
            "checks": {
                "document_information": "PASSED" if not is_unknown else "NOT_VERIFIED",
                "document_details": "PASSED" if (marks_res["status"] == "PASSED" and req_res["status"] == "PASSED") else ("SUSPICIOUS" if marks_res["status"] == "SUSPICIOUS" else "NOT_VERIFIED"),
                "numerical_consistency": marks_res["status"],
                "identifier_validation": id_res["status"],
                "issuer_validation": issuer_res["status"],
                "date_validation": date_res["status"],
                "qr_verification": qr_res["status"],
                "barcode_verification": barcode_res["status"],
                "digital_signature": digital_sig_res["status"],
                "metadata": metadata_res["status"]
            },
            "evidence": {
                "classification": class_details,
                "marks_and_percentage": marks_res,
                "required_fields": req_res,
                "identifiers": id_res,
                "issuer": issuer_res,
                "dates": date_res,
                "qr": qr_res,
                "barcode": barcode_res,
                "digital_signature": digital_sig_res,
                "signatory_block": signatory_res,
                "metadata": metadata_res
            }
        }

rule_engine = RuleEngine()
