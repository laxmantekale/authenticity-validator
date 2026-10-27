import re
from typing import Dict, Any, Tuple


class IdentifierRules:
    """
    Format and structure validators for official document identifiers across universal categories.
    """

    @staticmethod
    def validate_pan(pan_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Indian Permanent Account Number (PAN).
        Format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F).
        """
        if not pan_str:
            return False, "Identifier missing", {}

        clean_pan = pan_str.strip().upper().replace(" ", "").replace("-", "")
        # Check if masked
        if clean_pan.startswith("XXXXX") and len(clean_pan) == 10:
            return True, "Masked PAN format valid", {"masked": True, "pan": clean_pan}

        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if not re.match(pattern, clean_pan):
            return False, "Invalid PAN format (expected 5 letters, 4 digits, 1 letter)", {"pan": clean_pan}

        entity_type_char = clean_pan[3]
        valid_entities = {
            'P': 'Individual',
            'C': 'Company',
            'H': 'Hindu Undivided Family (HUF)',
            'F': 'Partnership Firm / LLP',
            'A': 'Association of Persons (AOP)',
            'T': 'Trust',
            'B': 'Body of Individuals (BOI)',
            'L': 'Local Authority',
            'J': 'Artificial Juridical Person',
            'G': 'Government Agency'
        }
        entity_name = valid_entities.get(entity_type_char, "Other Entity")

        return True, f"Valid PAN format ({entity_name})", {
            "pan": clean_pan,
            "entity_code": entity_type_char,
            "entity_type": entity_name
        }

    @staticmethod
    def validate_aadhaar(aadhaar_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Aadhaar Number format (12 digits) or Masked Aadhaar (XXXX XXXX 1234).
        """
        if not aadhaar_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', aadhaar_str.strip().upper())

        # Masked Aadhaar check
        if re.match(r'^(?:X{8}|[X]{4}[X]{4})(\d{4})$', clean):
            return True, "Masked Aadhaar format valid", {"masked": True, "last_four": clean[-4:]}

        # 12-digit standard check
        if re.match(r'^[2-9][0-9]{11}$', clean):
            masked_rep = f"XXXX XXXX {clean[-4:]}"
            return True, "Valid 12-digit Aadhaar format", {"masked": False, "masked_display": masked_rep}

        return False, "Invalid Aadhaar identifier pattern", {"raw": aadhaar_str}

    @staticmethod
    def validate_gstin(gstin_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Indian GST Identification Number (GSTIN).
        Format: 2 state digits + 10 PAN chars + 1 entity num + 'Z' + 1 checksum char (15 chars total).
        """
        if not gstin_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', gstin_str.strip().upper())
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

        if not re.match(pattern, clean):
            return False, "Invalid GSTIN pattern (expected 15 alphanumeric characters with state code and PAN)", {"gstin": clean}

        state_code = clean[:2]
        pan_part = clean[2:12]
        is_pan_valid, _, _ = IdentifierRules.validate_pan(pan_part)

        if not is_pan_valid:
            return False, "Invalid embedded PAN inside GSTIN", {"gstin": clean, "pan_part": pan_part}

        return True, "Valid GSTIN structure and embedded PAN", {
            "gstin": clean,
            "state_code": state_code,
            "embedded_pan": pan_part
        }

    @staticmethod
    def validate_cin(cin_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Corporate Identification Number (CIN).
        Format: U/L + 5 digits + 2 state letters + 4 year digits + 3 industry letters + 6 registration digits.
        Example: U72200MH2020PTC123456
        """
        if not cin_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', cin_str.strip().upper())
        pattern = r"^[UL][0-9]{5}[A-Z]{2}[12][0-9]{3}[A-Z]{3}[0-9]{6}$"

        if re.match(pattern, clean):
            return True, "Valid Corporate Identification Number (CIN)", {
                "cin": clean,
                "listing_status": "Listed" if clean[0] == "L" else "Unlisted",
                "state_code": clean[6:8],
                "incorporation_year": clean[8:12]
            }

        return False, "Invalid CIN pattern (expected 21 alphanumeric characters)", {"raw": cin_str}

    @staticmethod
    def validate_udyam(udyam_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates MSME Udyam Registration Number.
        Format: UDYAM-XX-00-0000000 (e.g. UDYAM-MH-12-0012345)
        """
        if not udyam_str:
            return False, "Identifier missing", {}

        clean = udyam_str.strip().upper()
        pattern = r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$"

        if re.match(pattern, clean):
            parts = clean.split("-")
            return True, "Valid Udyam Registration Number", {
                "udyam_number": clean,
                "state_code": parts[1],
                "district_code": parts[2]
            }

        return False, "Invalid Udyam Registration pattern", {"raw": udyam_str}

    @staticmethod
    def validate_ifsc(ifsc_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Bank IFSC Code.
        Format: 4 letters + 0 + 6 alphanumeric (e.g. SBIN0001234, HDFC0000123).
        """
        if not ifsc_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', ifsc_str.strip().upper())
        pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"

        if re.match(pattern, clean):
            return True, f"Valid IFSC code structure ({clean[:4]})", {"ifsc": clean, "bank_prefix": clean[:4]}

        return False, "Invalid IFSC code structure", {"raw": ifsc_str}

    @staticmethod
    def validate_passport(passport_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Indian Passport Number.
        Format: 1 uppercase letter followed by 7 digits.
        """
        if not passport_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', passport_str.strip().upper())
        pattern = r"^[A-Z][0-9]{7}$"

        if not re.match(pattern, clean):
            return False, "Invalid Indian Passport pattern (expected 1 letter followed by 7 digits)", {"passport": clean}

        return True, "Valid Indian Passport format", {"passport": clean}

    @staticmethod
    def validate_driving_licence(dl_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Indian Driving Licence (DL).
        Format: 2 state letters + 2 RTO digits + 4 year digits + 7 serial digits.
        """
        if not dl_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-\/]', '', dl_str.strip().upper())
        pattern = r"^[A-Z]{2}[0-9]{2}[0-9]{4}[0-9]{7}$"

        if re.match(pattern, clean):
            return True, "Valid standard Indian Driving Licence format", {
                "dl_number": clean,
                "state_code": clean[:2],
                "rto_code": clean[2:4],
                "issue_year": clean[4:8]
            }

        if len(clean) >= 10 and re.match(r"^[A-Z]{2}[0-9A-Z]{8,14}$", clean):
            return True, "Valid regional Driving Licence pattern", {"dl_number": clean}

        return False, "Invalid Driving Licence identifier pattern", {"raw": dl_str}

    @staticmethod
    def validate_voter_id(epic_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Election Commission Voter ID (EPIC).
        Format: 3 letters + 7 digits.
        """
        if not epic_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', epic_str.strip().upper())
        pattern = r"^[A-Z]{3}[0-9]{7}$"

        if re.match(pattern, clean):
            return True, "Valid Election Commission EPIC Voter ID format", {"epic_number": clean}

        return False, "Invalid Voter ID format", {"raw": epic_str}

    @staticmethod
    def validate_vehicle_rc(rc_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates Vehicle Registration Certificate (RC) Number.
        """
        if not rc_str:
            return False, "Identifier missing", {}

        clean = re.sub(r'[\s\-]', '', rc_str.strip().upper())
        pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$"

        if re.match(pattern, clean):
            return True, "Valid Vehicle Registration number format", {"rc_number": clean}

        return False, "Invalid Vehicle Registration number pattern", {"raw": rc_str}

    @staticmethod
    def validate_academic_identifier(id_str: str, id_type: str = "Roll/Seat Number") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates academic roll numbers, seat numbers, registration numbers, enrollment numbers.
        """
        if not id_str:
            return True, f"{id_type} not provided (Optional check)", {"status": "NOT_APPLICABLE"}

        clean = id_str.strip().upper()
        if re.match(r"^[A-Z0-9\-\/]{3,24}$", clean):
            return True, f"Valid {id_type} format", {"identifier": clean}

        return False, f"Invalid {id_type} format", {"raw": id_str}

    @classmethod
    def validate_document_identifiers(cls, doc_type: str, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes identifier validation based on the classified document type.
        """
        results = {
            "status": "PASSED",
            "message": "All present identifiers validated successfully",
            "details": {}
        }

        # Identity Checks
        if doc_type in ["PAN Card", "e-PAN", "Business PAN Document"]:
            pan = extracted_fields.get("identity_number") or extracted_fields.get("pan_number") or extracted_fields.get("document_number")
            if pan:
                valid, msg, d = cls.validate_pan(pan)
                results["details"]["pan_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg
            else:
                results["status"] = "NOT_APPLICABLE"
                results["message"] = "PAN identifier not found on document"

        elif doc_type in ["Aadhaar Card", "Masked Aadhaar Card", "e-Aadhaar"]:
            aadhaar = extracted_fields.get("identity_number") or extracted_fields.get("aadhaar_number") or extracted_fields.get("document_number")
            if aadhaar:
                valid, msg, d = cls.validate_aadhaar(aadhaar)
                results["details"]["aadhaar_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg
            else:
                results["status"] = "NOT_APPLICABLE"
                results["message"] = "Aadhaar identifier not found on document"

        elif doc_type == "Passport":
            pass_no = extracted_fields.get("document_number") or extracted_fields.get("identity_number")
            if pass_no:
                valid, msg, d = cls.validate_passport(pass_no)
                results["details"]["passport_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type == "Driving Licence":
            dl_no = extracted_fields.get("document_number") or extracted_fields.get("identity_number")
            if dl_no:
                valid, msg, d = cls.validate_driving_licence(dl_no)
                results["details"]["dl_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type == "Voter ID":
            voter_no = extracted_fields.get("document_number") or extracted_fields.get("identity_number")
            if voter_no:
                valid, msg, d = cls.validate_voter_id(voter_no)
                results["details"]["voter_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type in ["GST Certificate", "GST Registration Certificate"]:
            gstin = extracted_fields.get("document_number") or extracted_fields.get("identity_number") or extracted_fields.get("gstin")
            if gstin:
                valid, msg, d = cls.validate_gstin(gstin)
                results["details"]["gstin_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type == "Certificate of Incorporation":
            cin = extracted_fields.get("cin_number") or extracted_fields.get("document_number")
            if cin:
                valid, msg, d = cls.validate_cin(cin)
                results["details"]["cin_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type == "MSME/Udyam Certificate":
            udyam = extracted_fields.get("udyam_registration_number") or extracted_fields.get("document_number")
            if udyam:
                valid, msg, d = cls.validate_udyam(udyam)
                results["details"]["udyam_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        elif doc_type == "Bank Statement":
            ifsc = extracted_fields.get("ifsc_code")
            acc = extracted_fields.get("account_number")
            if ifsc:
                v, m, d = cls.validate_ifsc(ifsc)
                results["details"]["ifsc_validation"] = {"valid": v, "message": m, **d}
                if not v:
                    results["status"] = "FAILED"
                    results["message"] = m
            if acc and re.match(r"^[0-9]{9,18}$", acc):
                results["details"]["account_number_validation"] = {"valid": True, "masked": f"XXXXXX{acc[-4:]}"}

        elif doc_type in ["Vehicle Registration Certificate", "RC"]:
            rc_no = extracted_fields.get("document_number") or extracted_fields.get("identity_number")
            if rc_no:
                valid, msg, d = cls.validate_vehicle_rc(rc_no)
                results["details"]["rc_validation"] = {"valid": valid, "message": msg, **d}
                if not valid:
                    results["status"] = "FAILED"
                    results["message"] = msg

        else:
            # Academic / General Certificate Check
            seat_roll = extracted_fields.get("roll_number") or extracted_fields.get("seat_number")
            cert_no = extracted_fields.get("certificate_number") or extracted_fields.get("document_number")

            if seat_roll:
                v, m, d = cls.validate_academic_identifier(seat_roll, "Seat/Roll Number")
                results["details"]["seat_roll_validation"] = {"valid": v, "message": m, **d}
            if cert_no:
                v, m, d = cls.validate_academic_identifier(cert_no, "Certificate Number")
                results["details"]["cert_no_validation"] = {"valid": v, "message": m, **d}

        return results
