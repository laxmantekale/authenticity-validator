import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

class DateRules:
    """
    Validates dates, detects impossible calendar values, and checks chronological consistency.
    """

    MONTH_NAMES = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }

    DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    @classmethod
    def is_leap_year(cls, year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @classmethod
    def parse_date(cls, date_str: str) -> Tuple[Optional[datetime], bool, str]:
        """
        Parses a date string and verifies its calendar validity.
        Returns (parsed_datetime, is_valid, message).
        """
        if not date_str:
            return None, True, "No date provided"

        clean = date_str.strip()

        # 1. Standard numeric formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        m_num = re.search(r'(\d{1,4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,4})', clean)
        if m_num:
            p1, p2, p3 = int(m_num.group(1)), int(m_num.group(2)), int(m_num.group(3))

            if p1 > 1000:  # YYYY-MM-DD
                year, month, day = p1, p2, p3
            else:  # DD-MM-YYYY
                day, month, year = p1, p2, p3
                if year < 100:
                    year += 2000 if year < 50 else 1900

            # Check month validity
            if month < 1 or month > 12:
                return None, False, f"Impossible month: {month} in '{date_str}'"

            # Check day validity including leap year check
            max_days = cls.DAYS_IN_MONTH[month]
            if month == 2 and cls.is_leap_year(year):
                max_days = 29

            if day < 1 or day > max_days:
                return None, False, f"Impossible calendar date: {day}/{month}/{year} in '{date_str}'"

            try:
                dt = datetime(year, month, day)
                return dt, True, "Valid date"
            except ValueError as e:
                return None, False, f"Invalid date value: {e}"

        # 2. Textual month formats: 15 August 2023, Aug 15 2023
        m_txt = re.search(r'(\d{1,2})[\s\-]+([a-zA-Z]+)[\s\-]+(\d{4})', clean)
        if m_txt:
            day = int(m_txt.group(1))
            month_str = m_txt.group(2).lower()
            year = int(m_txt.group(3))

            month = cls.MONTH_NAMES.get(month_str)
            if not month:
                for k, v in cls.MONTH_NAMES.items():
                    if month_str.startswith(k):
                        month = v
                        break

            if not month:
                return None, False, f"Unrecognized month name '{m_txt.group(2)}'"

            max_days = cls.DAYS_IN_MONTH[month]
            if month == 2 and cls.is_leap_year(year):
                max_days = 29

            if day < 1 or day > max_days:
                return None, False, f"Impossible calendar date: {day} {month_str} {year}"

            try:
                dt = datetime(year, month, day)
                return dt, True, "Valid date"
            except ValueError as e:
                return None, False, f"Invalid date value: {e}"

        return None, True, "Date pattern could not be definitively structured"

    @classmethod
    def validate_date_consistency(cls, fields: Dict[str, Any], raw_text: str = None) -> Dict[str, Any]:
        """
        Validates calendar consistency across DOB, issue date, expiry date, academic year.
        """
        results = {
            "status": "PASSED",
            "message": "Date chronology is logically consistent",
            "details": {}
        }

        now = datetime.utcnow()
        dob_raw = fields.get("dob") or fields.get("date_of_birth")
        issue_raw = fields.get("issue_date") or fields.get("date")
        expiry_raw = fields.get("expiry_date") or fields.get("valid_till")

        # Fallback extraction from raw_text if present
        if raw_text:
            if not dob_raw:
                dob_m = re.search(r'(?:dob|date\s+of\s+birth|birth\s+date)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', raw_text, re.IGNORECASE)
                if dob_m:
                    dob_raw = dob_m.group(1).strip()
            if not issue_raw:
                issue_m = re.search(r'(?:date\s+of\s+issue|issue\s+date|issued\s+on)[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', raw_text, re.IGNORECASE)
                if issue_m:
                    issue_raw = issue_m.group(1).strip()
            if not expiry_raw:
                exp_m = re.search(r'(?:date\s+of\s+expiry|expiry\s+date|valid\s+(?:till|up\s*to|thru|to))[:.\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', raw_text, re.IGNORECASE)
                if exp_m:
                    expiry_raw = exp_m.group(1).strip()

        # 1. Parse individual dates
        dob_dt, dob_valid, dob_msg = cls.parse_date(dob_raw) if dob_raw else (None, True, "")
        issue_dt, issue_valid, issue_msg = cls.parse_date(issue_raw) if issue_raw else (None, True, "")
        expiry_dt, expiry_valid, expiry_msg = cls.parse_date(expiry_raw) if expiry_raw else (None, True, "")

        if not dob_valid:
            results["status"] = "SUSPICIOUS"
            results["message"] = f"Date error: {dob_msg}"
            results["details"]["dob_error"] = dob_msg
            return results

        if not issue_valid:
            results["status"] = "SUSPICIOUS"
            results["message"] = f"Date error: {issue_msg}"
            results["details"]["issue_error"] = issue_msg
            return results

        if not expiry_valid:
            results["status"] = "SUSPICIOUS"
            results["message"] = f"Date error: {expiry_msg}"
            results["details"]["expiry_error"] = expiry_msg
            return results

        # 2. Future DOB check
        if dob_dt and dob_dt > now:
            results["status"] = "SUSPICIOUS"
            results["message"] = f"Impossible Date of Birth in the future ({dob_dt.strftime('%d/%m/%Y')})"
            results["details"]["future_dob"] = True
            return results

        # 3. Issue vs Expiry Chronology
        if issue_dt and expiry_dt:
            if issue_dt > expiry_dt:
                results["status"] = "SUSPICIOUS"
                results["message"] = f"Contradictory dates: Issue date ({issue_dt.strftime('%d/%m/%Y')}) is after Expiry date ({expiry_dt.strftime('%d/%m/%Y')})"
                results["details"]["inverted_validity"] = True
                return results

        # 4. DOB vs Issue Date sanity (Must be born before document issuance)
        if dob_dt and issue_dt and dob_raw != issue_raw:
            if dob_dt > issue_dt:
                results["status"] = "SUSPICIOUS"
                results["message"] = f"Contradictory dates: Date of birth is after document issue date"
                results["details"]["dob_after_issue"] = True
                return results

        results["details"]["parsed_dates"] = {
            "dob": dob_dt.strftime("%Y-%m-%d") if dob_dt else None,
            "issue_date": issue_dt.strftime("%Y-%m-%d") if issue_dt else None,
            "expiry_date": expiry_dt.strftime("%Y-%m-%d") if expiry_dt else None
        }

        return results
