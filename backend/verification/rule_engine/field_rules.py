import re
from typing import Dict, Any, List, Tuple
from verification.registry import DocumentTypeRegistry


class FieldRules:
    """
    Validates numerical consistency, marks, percentages, totals, and field relationships
    across Academic, Financial, Employment, and universal document types.
    """

    @classmethod
    def validate_marks_and_percentage(cls, fields: Dict[str, Any], raw_text: str = "", doc_type: str = None) -> Dict[str, Any]:
        """
        Universal numerical consistency validator:
        - Validates academic marks, percentages, CGPA.
        - Validates financial invoice totals (subtotal + tax == total).
        - Validates salary slip breakdown (basic + allowances - deductions == net pay).
        """
        results = {
            "status": "PASSED",
            "message": "Numerical values and calculations are logically consistent",
            "details": {}
        }

        # Check profile from DocumentTypeRegistry
        profile = DocumentTypeRegistry.get_profile(doc_type) if doc_type else {}

        # ---------------------------------------------------------
        # 1. FINANCIAL TOTALS VALIDATION (Invoices, Receipts, POs)
        # ---------------------------------------------------------
        if profile.get("has_financial_totals") or profile.get("category") == "Financial":
            subtotal = fields.get("subtotal")
            tax = fields.get("tax_amount")
            total = fields.get("total_amount") or fields.get("amount")

            # Fallback regex extraction from text if not in fields
            if subtotal is None and raw_text:
                m_sub = re.search(r'(?:sub\s*total|subtotal|taxable\s*value)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', raw_text, re.IGNORECASE)
                if m_sub:
                    try:
                        subtotal = float(m_sub.group(1).replace(",", ""))
                    except ValueError:
                        pass

            if tax is None and raw_text:
                m_tax = re.search(r'(?:total\s*tax|tax\s*amount|gst\s*amount|vat\s*amount)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', raw_text, re.IGNORECASE)
                if m_tax:
                    try:
                        tax = float(m_tax.group(1).replace(",", ""))
                    except ValueError:
                        pass

            if total is None and raw_text:
                m_tot = re.search(r'(?<!sub)(?<!sub\s)\b(?:grand\s*total|total\s*amount|invoice\s*total|net\s*amount|total)\b[:.\s]*(?:rs\.?|inr|\$|₹)?\s*([\d,]+\.?\d*)', raw_text, re.IGNORECASE)
                if m_tot:
                    try:
                        total = float(m_tot.group(1).replace(",", ""))
                    except ValueError:
                        pass

            if subtotal is not None and tax is not None and total is not None:
                expected_tot = round(subtotal + tax, 2)
                diff = abs(total - expected_tot)
                results["details"]["subtotal"] = subtotal
                results["details"]["tax_amount"] = tax
                results["details"]["stated_total"] = total
                results["details"]["calculated_total"] = expected_tot
                results["details"]["discrepancy"] = round(diff, 2)

                if diff > 2.0:
                    results["status"] = "SUSPICIOUS"
                    results["message"] = f"Financial arithmetic discrepancy: Stated total ({total}) does not match subtotal + tax ({subtotal} + {tax} = {expected_tot})"
                    results["details"]["financial_mismatch"] = True
                    return results

        # ---------------------------------------------------------
        # 2. SALARY BREAKDOWN VALIDATION (Salary Slips)
        # ---------------------------------------------------------
        if profile.get("has_salary_breakdown") or doc_type == "Salary Slip":
            basic = fields.get("basic_salary")
            hra = fields.get("hra") or 0.0
            allowances = fields.get("allowances") or 0.0
            deductions = fields.get("deductions") or 0.0
            net_pay = fields.get("net_pay")

            if basic is not None and net_pay is not None and (hra > 0 or allowances > 0 or deductions > 0):
                expected_net = round(basic + hra + allowances - deductions, 2)
                diff = abs(net_pay - expected_net)
                results["details"]["basic_salary"] = basic
                results["details"]["deductions"] = deductions
                results["details"]["stated_net_pay"] = net_pay
                results["details"]["calculated_net_pay"] = expected_net
                results["details"]["discrepancy"] = round(diff, 2)

                if diff > 5.0:
                    results["status"] = "SUSPICIOUS"
                    results["message"] = f"Salary arithmetic discrepancy: Stated net pay ({net_pay}) does not match basic + allowances - deductions ({expected_net})"
                    results["details"]["salary_mismatch"] = True
                    return results

        # ---------------------------------------------------------
        # 3. ACADEMIC MARKS & PERCENTAGES
        # ---------------------------------------------------------
        if doc_type and not profile.get("has_marks", False) and profile.get("category") not in ["Academic"]:
            if not profile.get("has_financial_totals") and not profile.get("has_salary_breakdown"):
                return {
                    "status": "NOT_APPLICABLE",
                    "message": f"Numerical marks verification not applicable for {doc_type}",
                    "details": {}
                }

        # Extracted marks
        obtained = fields.get("marks_obtained")
        maximum = fields.get("maximum_marks") or fields.get("total_marks")
        pct_str = fields.get("percentage")

        if (obtained is None or maximum is None) and raw_text:
            clean_text_for_marks = re.sub(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b', ' ', raw_text)
            clean_text_for_marks = re.sub(r'(?:no\.?|ref(?:erence)?\.?|g\.?r\.?|case|order|reg(?:istration)?)\s*[:.\s]*[A-Za-z0-9\-]*\d+[\/\\]\d+[A-Za-z0-9\-]*', ' ', clean_text_for_marks, flags=re.IGNORECASE)

            m_tot = re.search(r'(?:total\s*marks(?:\s*obtained)?|grand\s*total|marks\s*obtained|total\s*score)[:.\s]*(\d{2,4})\s*(?:[\/\\]|\s+out\s+of\s+)\s*(\d{2,4})', clean_text_for_marks, re.IGNORECASE)
            if not m_tot:
                m_tot = re.search(r'\b(?:marks|total|score)\s*[:.\s]+(\d{2,4})\s*(?:[\/\\]|\s+out\s+of\s+)\s*(\d{2,4})\b', clean_text_for_marks, re.IGNORECASE)
            if m_tot:
                obtained = float(m_tot.group(1))
                maximum = float(m_tot.group(2))

        if not pct_str and raw_text:
            m_pct = re.search(r'(\d{1,3}(?:\.\d{1,2})?)\s*%', raw_text)
            if m_pct:
                pct_str = m_pct.group(1)

        if obtained is not None and maximum is not None:
            try:
                obt = float(obtained)
                mx = float(maximum)

                results["details"]["marks_obtained"] = obt
                results["details"]["maximum_marks"] = mx

                # Check impossible marks (Obtained > Maximum)
                if obt > mx and mx > 0:
                    results["status"] = "SUSPICIOUS"
                    results["message"] = f"Impossible marks: Obtained marks ({obt}) exceed maximum marks ({mx})"
                    results["details"]["impossible_marks"] = True
                    return results

                # Percentage consistency check
                if pct_str and mx > 0:
                    clean_pct = float(re.sub(r'[^\d.]', '', str(pct_str)))
                    expected_pct = (obt / mx) * 100.0
                    diff = abs(clean_pct - expected_pct)

                    results["details"]["stated_percentage"] = clean_pct
                    results["details"]["calculated_percentage"] = round(expected_pct, 2)
                    results["details"]["discrepancy"] = round(diff, 2)

                    # Allow +/- 1.5% rounding difference
                    if diff > 1.5:
                        results["status"] = "SUSPICIOUS"
                        results["message"] = f"Numerical inconsistency: Stated percentage ({clean_pct}%) does not match calculated total ({obt}/{mx} = {expected_pct:.2f}%)"
                        results["details"]["percentage_mismatch"] = True
                        return results

            except (ValueError, TypeError):
                pass

        # CGPA Check
        cgpa = fields.get("cgpa") or fields.get("sgpa")
        if cgpa is not None:
            try:
                cgpa_val = float(re.sub(r'[^\d.]', '', str(cgpa)))
                results["details"]["cgpa"] = cgpa_val
                if cgpa_val > 10.0:
                    results["status"] = "SUSPICIOUS"
                    results["message"] = f"Impossible CGPA/SGPA value: {cgpa_val} (standard scale maximum is 10.0)"
                    results["details"]["impossible_cgpa"] = True
                    return results
            except (ValueError, TypeError):
                pass

        return results

    @classmethod
    def validate_required_fields_present(cls, doc_type: str, fields: Dict[str, Any], raw_text: str = "") -> Dict[str, Any]:
        """
        Validates presence of essential fields for a given document type based on DocumentTypeRegistry.
        Missing fields result in NOT_VERIFIED (never FORGED).
        """
        results = {
            "status": "PASSED",
            "message": "Essential document fields identified",
            "missing_fields": []
        }

        profile = DocumentTypeRegistry.get_profile(doc_type)
        req_fields = profile.get("required_fields", [])
        if not req_fields:
            return results

        missing = []
        for req in req_fields:
            val = fields.get(req)
            if val is not None and str(val).strip():
                continue

            # Check contextual aliases
            if req in ["student_name", "candidate_name", "name", "holder_name", "employee_name", "patient_name", "deponent_name"]:
                if fields.get("student_name") or fields.get("name") or fields.get("holder_name") or fields.get("employee_name") or fields.get("patient_name"):
                    continue
                if re.search(r'(?:certify\s+that|name|candidate|employee|patient|deponent)[:.\s]*[A-Za-z\s]{3,}', raw_text, re.IGNORECASE):
                    continue
                missing.append("Candidate/Entity Name")

            elif req in ["identity_number", "document_number"]:
                if fields.get("identity_number") or fields.get("document_number"):
                    continue
                if re.search(r'\b(?:[A-Z]{5}\d{4}[A-Z]|\d{4}\s*\d{4}\s*\d{4}|[A-Z]{3}\d{7}|[A-Z]{2}\d{13,15})\b', raw_text):
                    continue
                missing.append("Identity/Registration Number")

            elif req in ["seat_number", "marks_or_seat", "roll_number"]:
                if fields.get("seat_number") or fields.get("roll_number") or fields.get("marks_obtained"):
                    continue
                if re.search(r'(?:seat|roll|reg|prn|marks)[:.\s]*[A-Za-z0-9\-\/]{3,}', raw_text, re.IGNORECASE):
                    continue
                missing.append("Seat/Roll Number")

            elif req in ["total_amount", "amount", "net_pay"]:
                if fields.get("total_amount") or fields.get("amount") or fields.get("net_pay"):
                    continue
                if re.search(r'(?:total|amount|net\s*pay)[:.\s]*(?:rs\.?|inr|\$|₹)?\s*[\d,]+', raw_text, re.IGNORECASE):
                    continue
                missing.append("Total Amount")

            elif req in ["cin_number", "gstin", "udyam_registration_number"]:
                if fields.get(req):
                    continue
                missing.append(req.replace("_", " ").title())

        if missing:
            results["status"] = "NOT_VERIFIED"
            results["message"] = f"Document information is incomplete (missing: {', '.join(missing)})"
            results["missing_fields"] = missing

        return results
