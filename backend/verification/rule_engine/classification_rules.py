import re
import os
from typing import Dict, Any, Tuple, Optional

# Canonical Document Types with their Category Mapping
DOCUMENT_CATEGORIES = {
    # Academic / Education
    "10th Marksheet": "Academic",
    "10th Passing Certificate": "Academic",
    "12th Marksheet": "Academic",
    "12th Passing Certificate": "Academic",
    "Diploma Certificate": "Academic",
    "Diploma Marksheet": "Academic",
    "Degree Certificate": "Academic",
    "Provisional Degree Certificate": "Academic",
    "Engineering Degree Certificate": "Academic",
    "B.E. Certificate": "Academic",
    "B.Tech Certificate": "Academic",
    "BCA Certificate": "Academic",
    "B.Sc Certificate": "Academic",
    "B.Com Certificate": "Academic",
    "BBA Certificate": "Academic",
    "BA Certificate": "Academic",
    "MA Certificate": "Academic",
    "M.Sc Certificate": "Academic",
    "M.Com Certificate": "Academic",
    "MBA Certificate": "Academic",
    "MCA Certificate": "Academic",
    "M.Tech Certificate": "Academic",
    "PhD Certificate": "Academic",
    "Semester Marksheet": "Academic",
    "Semester Grade Card": "Academic",
    "Grade Card": "Academic",
    "Annual Marksheet": "Academic",
    "Consolidated Marksheet": "Academic",
    "Transcript": "Academic",
    "Bonafide Certificate": "Academic",
    "Leaving Certificate": "Academic",
    "Transfer Certificate": "Academic",
    "Character Certificate": "Academic",
    "Migration Certificate": "Academic",
    "Admission Letter": "Academic",
    "Admission Certificate": "Academic",
    "Enrollment Certificate": "Academic",
    "Registration Certificate": "Academic",
    "Examination Certificate": "Academic",
    "Scholarship Certificate": "Academic",
    "University Certificate": "Academic",
    "College Certificate": "Academic",
    "Board Certificate": "Academic",
    "Course Completion Certificate": "Academic",
    "Internship Certificate": "Academic",
    "Training Certificate": "Academic",

    # Maharashtra / Government Documents
    "Maharashtra State Board Document": "Government",
    "SPPU Document": "Academic",
    "Domicile Certificate": "Government",
    "Income Certificate": "Government",
    "Caste Certificate": "Government",
    "Caste Validity Certificate": "Government",
    "EWS Certificate": "Government",
    "Non-Creamy Layer Certificate": "Government",
    "Residence Certificate": "Government",
    "Nationality Certificate": "Government",
    "Birth Certificate": "Government",
    "Death Certificate": "Government",
    "Government Certificate": "Government",
    "Government Order": "Government",
    "Government Letter": "Government",
    "Revenue Department Document": "Government",

    # Identity Documents
    "Aadhaar Card": "Identity",
    "Masked Aadhaar Card": "Identity",
    "e-Aadhaar": "Identity",
    "PAN Card": "Identity",
    "e-PAN": "Identity",
    "Voter ID": "Identity",
    "Passport": "Identity",
    "Driving Licence": "Identity",
    "Ration Card": "Identity",

    # Financial / Banking Documents
    "Bank Statement": "Financial",
    "Bank Certificate": "Financial",
    "Bank Passbook": "Financial",
    "Bank Account Statement": "Financial",
    "Loan Document": "Financial",
    "Loan Sanction Letter": "Financial",
    "Loan Approval Letter": "Financial",
    "Fee Receipt": "Financial",
    "Payment Receipt": "Financial",
    "Fee Payment Certificate": "Financial",
    "Income/Financial Statement": "Financial",

    # Employment Documents
    "Offer Letter": "Employment",
    "Appointment Letter": "Employment",
    "Employment Certificate": "Employment",
    "Experience Certificate": "Employment",
    "Salary Certificate": "Employment",
    "Salary Slip": "Employment",
    "Relieving Letter": "Employment",
    "Service Certificate": "Employment",
    "Joining Letter": "Employment",
    "Promotion Letter": "Employment",

    # Medical Documents
    "Medical Certificate": "Medical",
    "Medical Fitness Certificate": "Medical",
    "Fitness Certificate": "Medical",
    "Vaccination Certificate": "Medical",
    "Health Certificate": "Medical",
    "Medical Report": "Medical",
    "Discharge Summary": "Medical",
    "Prescription": "Medical",
    "Laboratory Report": "Medical",
    "Diagnostic Report": "Medical",

    # Legal / Administrative Documents
    "Affidavit": "Legal",
    "Declaration": "Legal",
    "Agreement": "Legal",
    "Undertaking": "Legal",
    "Legal Notice": "Legal",
    "Official Notice": "Legal",
    "Authorization Letter": "Legal",
    "Consent Letter": "Legal",
    "Application Form": "Legal",
    "Government Form": "Legal",
    "Administrative Document": "Legal",
    "No Objection Certificate": "Legal",
    "Permission Letter": "Legal",

    # Property / Land Documents
    "7/12 Extract": "Property",
    "8A Extract": "Property",
    "Land Record": "Property",
    "Property Record": "Property",
    "Property Tax Receipt": "Property",
    "Property Tax Document": "Property",
    "Property Certificate": "Property",
    "Sale Deed": "Property",
    "Property Deed": "Property",
    "Mutation Record": "Property",
    "Mutation Certificate": "Property",
    "Land Ownership Certificate": "Property",
    "Revenue Record": "Property",

    # Transport / Vehicle Documents
    "Vehicle Registration Certificate": "Transport",
    "Vehicle Insurance Certificate": "Transport",
    "Pollution Under Control Certificate": "Transport",
    "PUC Certificate": "Transport",
    "Vehicle Fitness Certificate": "Transport",
    "Vehicle Permit": "Transport",
    "Transport Certificate": "Transport",

    # Insurance Documents
    "Insurance Policy": "Insurance",
    "Insurance Certificate": "Insurance",
    "Insurance Claim Document": "Insurance",
    "Insurance Premium Receipt": "Insurance",
    "Health Insurance Document": "Insurance",
    "Life Insurance Document": "Insurance",
    "Motor Insurance Document": "Insurance",

    # Business / Tax Documents
    "GST Certificate": "Business",
    "Certificate of Incorporation": "Business",
    "MSME/Udyam Certificate": "Business",
    "Purchase Order": "Business",
    "Invoice": "Financial",
    "Contract": "Legal",
    "GST Registration Certificate": "Business",
    "GST Return Document": "Business",
    "Company Registration Certificate": "Business",
    "Business Registration Certificate": "Business",
    "Trade Licence": "Business",
    "Shop Act Licence": "Business",
    "Business Certificate": "Business",
    "Tax Certificate": "Business",
    "Income Tax Document": "Business",
    "Business PAN Document": "Business",

    # Other Official Documents
    "Official Letter": "Other",
    "Official Certificate": "Other",
    "Official Receipt": "Other",
    "Application": "Other",
    "Registration Form": "Other",
    "Verification Certificate": "Other",
    "Authorization Certificate": "Other",
    "Membership Certificate": "Other",
    "University Form": "Other",
    "College Form": "Other",
    "Other Official Document": "Other",
    "Unknown Document": "Unknown"
}

# Alias Normalization Map
DOCUMENT_ALIAS_MAP = {
    "rc": "Vehicle Registration Certificate",
    "rc book": "Vehicle Registration Certificate",
    "vehicle rc": "Vehicle Registration Certificate",
    "vehicle registration": "Vehicle Registration Certificate",
    "registration certificate": "Vehicle Registration Certificate",
    "driving license": "Driving Licence",
    "dl": "Driving Licence",
    "driver licence": "Driving Licence",
    "pan": "PAN Card",
    "pan card": "PAN Card",
    "epan": "e-PAN",
    "e-pan": "e-PAN",
    "aadhaar": "Aadhaar Card",
    "aadhar": "Aadhaar Card",
    "aadhar card": "Aadhaar Card",
    "eaadhaar": "e-Aadhaar",
    "e-aadhaar": "e-Aadhaar",
    "masked aadhaar": "Masked Aadhaar Card",
    "7/12": "7/12 Extract",
    "7 12": "7/12 Extract",
    "7/12 extract": "7/12 Extract",
    "satbara": "7/12 Extract",
    "8a": "8A Extract",
    "8a extract": "8A Extract",
    "noc": "No Objection Certificate",
    "no objection certificate": "No Objection Certificate",
    "puc": "PUC Certificate",
    "puc certificate": "PUC Certificate",
    "ssc marksheet": "10th Marksheet",
    "10th marksheet": "10th Marksheet",
    "class 10 marksheet": "10th Marksheet",
    "class x marksheet": "10th Marksheet",
    "10th passing": "10th Passing Certificate",
    "10th certificate": "10th Passing Certificate",
    "hsc marksheet": "12th Marksheet",
    "12th marksheet": "12th Marksheet",
    "class 12 marksheet": "12th Marksheet",
    "class xii marksheet": "12th Marksheet",
    "12th passing": "12th Passing Certificate",
    "12th certificate": "12th Passing Certificate",
    "degree": "Degree Certificate",
    "degree certificate": "Degree Certificate",
    "provisional degree": "Provisional Degree Certificate",
    "be certificate": "B.E. Certificate",
    "btech certificate": "B.Tech Certificate",
    "engineering degree": "Engineering Degree Certificate",
    "bonafide": "Bonafide Certificate",
    "leaving": "Leaving Certificate",
    "transfer": "Transfer Certificate",
    "caste": "Caste Certificate",
    "income": "Income Certificate",
    "domicile": "Domicile Certificate",
    "bank statement": "Bank Statement",
    "salary slip": "Salary Slip",
    "payslip": "Salary Slip",
    "offer letter": "Offer Letter",
    "gst": "GST Certificate",
    "gst certificate": "GST Certificate",
    "voter id": "Voter ID",
    "epic": "Voter ID",
    "passport": "Passport"
}

# Weighted Evidence Rules for Automatic Document Identification
DOCUMENT_EVIDENCE_RULES = {
    "10th Marksheet": {
        "required_any": [
            r"secondary\s+school\s+examination",
            r"secondary\s+school\s+certificate",
            r"class\s+x\b",
            r"class\s+10\b",
            r"10th\s+(?:standard|marksheet|exam)",
            r"matriculation\s+examination",
            r"s\.?s\.?c\.?\s+(?:examination|marksheet)"
        ],
        "supporting": [
            r"board\s+of\s+secondary\s+education",
            r"cbse",
            r"icse",
            r"state\s+board",
            r"seat\s+no",
            r"roll\s+no",
            r"marks\s+statement",
            r"grand\s+total",
            r"percentage"
        ],
        "negative": [
            r"higher\s+secondary",
            r"class\s+xii\b",
            r"class\s+12\b",
            r"h\.?s\.?c\.?",
            r"bachelor\s+of",
            r"semester"
        ],
        "weight": 10
    },

    "10th Passing Certificate": {
        "required_any": [
            r"secondary\s+school\s+(?:passing\s+)?certificate",
            r"matriculation\s+passing\s+certificate",
            r"10th\s+passing\s+certificate"
        ],
        "supporting": [
            r"passed\s+the\s+secondary\s+school",
            r"conferred\s+upon",
            r"controller\s+of\s+examinations"
        ],
        "negative": [
            r"higher\s+secondary",
            r"marks\s+statement"
        ],
        "weight": 9
    },

    "12th Marksheet": {
        "required_any": [
            r"higher\s+secondary\s+(?:school\s+)?certificate",
            r"higher\s+secondary\s+examination",
            r"senior\s+school\s+certificate",
            r"class\s+xii\b",
            r"class\s+12\b",
            r"12th\s+(?:standard|marksheet|exam)",
            r"h\.?s\.?c\.?\s+(?:examination|marksheet)",
            r"intermediate\s+examination"
        ],
        "supporting": [
            r"board\s+of\s+secondary\s+and\s+higher\s+secondary",
            r"cbse",
            r"hsc\s+board",
            r"physics",
            r"chemistry",
            r"mathematics",
            r"stream\s*:\s*science",
            r"seat\s+no",
            r"roll\s+no"
        ],
        "negative": [
            r"secondary\s+school\s+examination\s+20",
            r"class\s+x\b",
            r"matriculation",
            r"bachelor\s+of"
        ],
        "weight": 10
    },

    "12th Passing Certificate": {
        "required_any": [
            r"higher\s+secondary\s+passing\s+certificate",
            r"senior\s+school\s+passing\s+certificate",
            r"12th\s+passing\s+certificate"
        ],
        "supporting": [
            r"passed\s+the\s+higher\s+secondary",
            r"divisional\s+board",
            r"secretary"
        ],
        "negative": [
            r"secondary\s+school\s+certificate",
            r"marks\s+statement"
        ],
        "weight": 9
    },

    "Degree Certificate": {
        "required_any": [
            r"bachelor\s+of\s+[a-z\s]+",
            r"master\s+of\s+[a-z\s]+",
            r"doctor\s+of\s+philosophy",
            r"degree\s+of\s+bachelor",
            r"degree\s+of\s+master",
            r"hereby\s+confers\s+(?:on|upon)",
            r"convocation",
            r"under\s+the\s+seal\s+of\s+the\s+university"
        ],
        "supporting": [
            r"university\s+of",
            r"institute\s+of\s+technology",
            r"vice[- ]chancellor",
            r"senate",
            r"chancellor",
            r"first\s+class\s+with\s+distinction"
        ],
        "negative": [
            r"provisional\s+certificate",
            r"higher\s+secondary",
            r"school\s+leaving"
        ],
        "weight": 10
    },

    "Provisional Degree Certificate": {
        "required_any": [
            r"provisional\s+degree\s+certificate",
            r"provisional\s+certificate",
            r"provisional\s+passing\s+certificate"
        ],
        "supporting": [
            r"passed\s+the\s+examination\s+for\s+the\s+degree",
            r"eligible\s+for\s+the\s+award\s+of\s+degree",
            r"controller\s+of\s+examinations"
        ],
        "negative": [],
        "weight": 9
    },

    "Diploma Certificate": {
        "required_any": [
            r"diploma\s+in\s+[a-z\s]+",
            r"board\s+of\s+technical\s+education",
            r"msbte",
            r"polytechnic"
        ],
        "supporting": [
            r"director\s+of\s+technical\s+education",
            r"curriculum",
            r"semester"
        ],
        "negative": [
            r"degree\s+of\s+bachelor"
        ],
        "weight": 9
    },

    "Semester Marksheet": {
        "required_any": [
            r"statement\s+of\s+marks",
            r"statement\s+of\s+grades",
            r"semester\s+[i|v|x|0-9]+(?:\s+examination|\s+grade\s+card|\s+marksheet)",
            r"marksheet\b",
            r"sgpa\b",
            r"cgpa\b",
            r"credit\s+grade\s+system",
            r"performance\s+record"
        ],
        "supporting": [
            r"course\s+code",
            r"credits\s+earned",
            r"grade\s+points",
            r"university\s+of",
            r"controller\s+of\s+examinations"
        ],
        "negative": [
            r"higher\s+secondary",
            r"secondary\s+school\s+certificate"
        ],
        "weight": 9
    },

    "Transcript": {
        "required_any": [
            r"official\s+transcript",
            r"academic\s+transcript",
            r"cumulative\s+transcript",
            r"transcript\s+of\s+academic\s+records"
        ],
        "supporting": [
            r"medium\s+of\s+instruction",
            r"course\s+structure",
            r"overall\s+cgpa",
            r"registrar"
        ],
        "negative": [],
        "weight": 9
    },

    "Bonafide Certificate": {
        "required_any": [
            r"bonafide\s+certificate",
            r"bonafide\s+student",
            r"is\s+a\s+bonafide\s+student"
        ],
        "supporting": [
            r"studying\s+in",
            r"academic\s+year",
            r"principal\s*\/",
            r"head\s+of\s+institution"
        ],
        "negative": [],
        "weight": 8
    },

    "Leaving Certificate": {
        "required_any": [
            r"school\s+leaving\s+certificate",
            r"college\s+leaving\s+certificate",
            r"leaving\s+certificate",
            r"slc\b",
            r"clc\b"
        ],
        "supporting": [
            r"date\s+of\s+leaving",
            r"reason\s+for\s+leaving",
            r"conduct\s+and\s+character",
            r"general\s+register\s+no"
        ],
        "negative": [],
        "weight": 8
    },

    "Transfer Certificate": {
        "required_any": [
            r"transfer\s+certificate",
            r"tc\s+no",
            r"college\s+transfer\s+certificate"
        ],
        "supporting": [
            r"admitted\s+to\s+class",
            r"fees\s+paid\s+upto",
            r"principal"
        ],
        "negative": [],
        "weight": 8
    },

    "Migration Certificate": {
        "required_any": [
            r"migration\s+certificate",
            r"inter[- ]university\s+migration"
        ],
        "supporting": [
            r"has\s+no\s+objection\s+to\s+his\/her\s+continuing\s+studies",
            r"registrar"
        ],
        "negative": [],
        "weight": 8
    },

    "PAN Card": {
        "required_any": [
            r"income\s+tax\s+department",
            r"permanent\s+account\s+number",
            r"govt\.?\s+of\s+india\s+income\s+tax",
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
        ],
        "supporting": [
            r"father'?s\s+name",
            r"date\s+of\s+birth",
            r"signature",
            r"incometaxindia"
        ],
        "negative": [
            r"unique\s+identification\s+authority",
            r"aadhaar"
        ],
        "weight": 10
    },

    "Aadhaar Card": {
        "required_any": [
            r"unique\s+identification\s+authority\s+of\s+india",
            r"uidai\b",
            r"mera\s+aadhaar",
            r"meri\s+pehchan",
            r"\b\d{4}\s+\d{4}\s+\d{4}\b",
            r"\bxxxx\s+xxxx\s+\d{4}\b"
        ],
        "supporting": [
            r"government\s+of\s+india",
            r"enrollment\s+no",
            r"dob\s*:",
            r"gender\s*:",
            r"vid\s*:"
        ],
        "negative": [
            r"income\s+tax\s+department",
            r"permanent\s+account\s+number"
        ],
        "weight": 10
    },

    "Voter ID": {
        "required_any": [
            r"election\s+commission\s+of\s+india",
            r"elector'?s\s+photo\s+identity\s+card",
            r"voter\s+identity\s+card",
            r"epic\s+no",
            r"\b[A-Z]{3}[0-9]{7}\b"
        ],
        "supporting": [
            r"elector\s+name",
            r"father'?s\s+name",
            r"constituency",
            r"electoral\s+registration\s+officer"
        ],
        "negative": [],
        "weight": 9
    },

    "Passport": {
        "required_any": [
            r"republic\s+of\s+india\s+passport",
            r"passport\s+no",
            r"type\s+p\s+ind",
            r"p<ind"
        ],
        "supporting": [
            r"nationality\s*:\s*indian",
            r"place\s+of\s+issue",
            r"place\s+of\s+birth",
            r"date\s+of\s+expiry"
        ],
        "negative": [],
        "weight": 10
    },

    "Driving Licence": {
        "required_any": [
            r"driving\s+licen[cs]e",
            r"motor\s+vehicles\s+department",
            r"union\s+of\s+india\s+driving",
            r"dl\s+no",
            r"rto\s+maharashtra"
        ],
        "supporting": [
            r"licensing\s+authority",
            r"cov\s+class\s+of\s+vehicle",
            r"mcwg",
            r"lmv",
            r"valid\s+till",
            r"transport"
        ],
        "negative": [],
        "weight": 9
    },

    "Caste Certificate": {
        "required_any": [
            r"caste\s+certificate",
            r"scheduled\s+caste",
            r"scheduled\s+tribe",
            r"other\s+backward\s+class",
            r"certificate\s+of\s+caste"
        ],
        "supporting": [
            r"tahasildar",
            r"sub[- ]divisional\s+magistrate",
            r"competent\s+authority",
            r"district\s+magistrate",
            r"ordinance"
        ],
        "negative": [
            r"validity\s+certificate",
            r"scrutiny\s+committee"
        ],
        "weight": 9
    },

    "Caste Validity Certificate": {
        "required_any": [
            r"caste\s+validity\s+certificate",
            r"scrutiny\s+committee",
            r"verification\s+of\s+caste\s+certificate",
            r"social\s+justice\s+department"
        ],
        "supporting": [
            r"divisional\s+caste\s+scrutiny",
            r"member\s+secretary",
            r"joint\s+commissioner"
        ],
        "negative": [],
        "weight": 9
    },

    "Income Certificate": {
        "required_any": [
            r"income\s+certificate",
            r"annual\s+income\s+certificate",
            r"certificate\s+of\s+annual\s+family\s+income"
        ],
        "supporting": [
            r"revenue\s+officer",
            r"tahasildar",
            r"taluk",
            r"rs\.?\s*[0-9,]+",
            r"financial\s+year"
        ],
        "negative": [],
        "weight": 9
    },

    "Domicile Certificate": {
        "required_any": [
            r"domicile\s+certificate",
            r"residence\s+certificate",
            r"domicile\s+of\s+maharashtra",
            r"certificate\s+of\s+age,?\s+nationality\s+and\s+domicile",
            r"age,\s+nationality\s+and\s+domicile",
            r"domicile\s+in\s+the\s+state"
        ],
        "issuers": [
            r"office\s+of\s+tehsildar",
            r"office\s+of\s+the\s+tahasildar",
            r"tahasildar",
            r"tehsildar",
            r"sub[- ]divisional\s+officer",
            r"state\s+of\s+maharashtra"
        ],
        "identifiers": [
            r"serial\s*no",
            r"certificate\s*no",
            r"application\s*no"
        ],
        "supporting": [
            r"citizen\s+of\s+india",
            r"residing\s+at",
            r"sub[- ]divisional\s+officer",
            r"tahasildar",
            r"tehsildar",
            r"district\s*:",
            r"taluka\s*:"
        ],
        "negative": [],
        "weight": 9
    },

    "EWS Certificate": {
        "required_any": [
            r"economically\s+weaker\s+sections",
            r"ews\s+certificate",
            r"income\s+and\s+asset\s+certificate"
        ],
        "supporting": [
            r"government\s+of\s+india",
            r"financial\s+year",
            r"family\s+income\s+is\s+below"
        ],
        "negative": [],
        "weight": 9
    },

    "Non-Creamy Layer Certificate": {
        "required_any": [
            r"non[- ]creamy\s+layer\s+certificate",
            r"does\s+not\s+belong\s+to\s+the\s+creamy\s+layer"
        ],
        "supporting": [
            r"other\s+backward\s+classes",
            r"valid\s+upto",
            r"tahasildar"
        ],
        "negative": [],
        "weight": 9
    },

    "7/12 Extract": {
        "required_any": [
            r"7\/12\s+extract",
            r"village\s+form\s+no\.?\s*7",
            r"gaon\s+namuna\s+7",
            r"satbara",
            r"adhikar\s+abhilekh"
        ],
        "supporting": [
            r"gat\s+no",
            r"survey\s+no",
            r"hector",
            r"aakar",
            r"potkharab",
            r"maharashtra\s+land\s+revenue"
        ],
        "negative": [],
        "weight": 10
    },

    "Bank Statement": {
        "required_any": [
            r"account\s+statement",
            r"bank\s+statement",
            r"statement\s+of\s+account",
            r"transaction\s+history"
        ],
        "supporting": [
            r"account\s+number",
            r"ifsc\s+code",
            r"opening\s+balance",
            r"closing\s+balance",
            r"debit",
            r"credit",
            r"branch\s+name"
        ],
        "negative": [],
        "weight": 9
    },

    "Fee Receipt": {
        "required_any": [
            r"fee\s+receipt",
            r"payment\s+receipt",
            r"tuition\s+fee\s+receipt",
            r"receipt\s+voucher"
        ],
        "supporting": [
            r"amount\s+received",
            r"receipt\s+no",
            r"student\s+id",
            r"academic\s+year",
            r"authorized\s+signatory"
        ],
        "negative": [],
        "weight": 8
    },

    "Offer Letter": {
        "required_any": [
            r"offer\s+letter",
            r"letter\s+of\s+offer",
            r"we\s+are\s+pleased\s+to\s+offer",
            r"appointment\s+letter",
            r"terms\s+of\s+employment"
        ],
        "supporting": [
            r"designation",
            r"date\s+of\s+joining",
            r"compensation",
            r"ctc",
            r"human\s+resources",
            r"reporting\s+manager"
        ],
        "negative": [],
        "weight": 9
    },

    "Experience Certificate": {
        "required_any": [
            r"experience\s+certificate",
            r"service\s+certificate",
            r"to\s+whomsoever\s+it\s+may\s+concern",
            r"has\s+worked\s+with\s+us"
        ],
        "supporting": [
            r"worked\s+as",
            r"period\s+from",
            r"relieving\s+date",
            r"conduct\s+and\s+character"
        ],
        "negative": [],
        "weight": 8
    },

    "Salary Slip": {
        "required_any": [
            r"salary\s+slip",
            r"pay\s+slip",
            r"payslip\s+for\s+the\s+month",
            r"earnings\s+and\s+deductions"
        ],
        "supporting": [
            r"basic\s+pay",
            r"hra\b",
            r"provident\s+fund",
            r"net\s+pay",
            r"gross\s+salary",
            r"employee\s+id"
        ],
        "negative": [],
        "weight": 9
    },

    "Medical Certificate": {
        "required_any": [
            r"medical\s+certificate",
            r"medical\s+fitness\s+certificate",
            r"certificate\s+of\s+medical\s+fitness",
            r"under\s+my\s+medical\s+care"
        ],
        "supporting": [
            r"reg(?:istration)?\s*no",
            r"registered\s+medical\s+practitioner",
            r"fit\s+to\s+resume\s+duties",
            r"suffering\s+from"
        ],
        "negative": [],
        "weight": 8
    },

    "GST Certificate": {
        "required_any": [
            r"goods\s+and\s+services\s+tax",
            r"gstin\b",
            r"registration\s+certificate\s+under\s+gst",
            r"form\s+gst\s+reg[- ]06"
        ],
        "supporting": [
            r"legal\s+name",
            r"trade\s+name",
            r"constitution\s+of\s+business",
            r"period\s+of\s+validity",
            r"jurisdictional\s+office"
        ],
        "negative": [],
        "weight": 10
    },

    "No Objection Certificate": {
        "required_any": [
            r"no\s+objection\s+certificate",
            r"\bnoc\b",
            r"has\s+no\s+objection\s+whatsoever"
        ],
        "supporting": [
            r"competent\s+authority",
            r"issued\s+for\s+the\s+purpose\s+of",
            r"authorized\s+signatory"
        ],
        "negative": [],
        "weight": 8
    },

    "Affidavit": {
        "required_any": [
            r"affidavit",
            r"sworn\s+before\s+me",
            r"solemnly\s+affirm\s+and\s+state",
            r"before\s+the\s+notary\s+public"
        ],
        "supporting": [
            r"deponent",
            r"notary\s+advocate",
            r"verification\s+clause",
            r"stamp\s+paper"
        ],
        "negative": [],
        "weight": 9
    },

    "Invoice": {
        "required_any": [
            r"tax\s+invoice",
            r"commercial\s+invoice",
            r"bill\s+of\s+supply",
            r"invoice\s+no"
        ],
        "supporting": [
            r"subtotal",
            r"cgst",
            r"sgst",
            r"igst",
            r"total\s+amount",
            r"billed\s+to",
            r"hsn\/?sac"
        ],
        "negative": [
            r"statement\s+of\s+marks",
            r"examination"
        ],
        "weight": 9
    },

    "Certificate of Incorporation": {
        "required_any": [
            r"certificate\s+of\s+incorporation",
            r"corporate\s+identity\s+number",
            r"registrar\s+of\s+companies",
            r"companies\s+act"
        ],
        "supporting": [
            r"cin\b",
            r"ministry\s+of\s+corporate\s+affairs",
            r"pursuant\s+to\s+sub-section",
            r"seal\s+of\s+the\s+registrar"
        ],
        "negative": [],
        "weight": 10
    },

    "MSME/Udyam Certificate": {
        "required_any": [
            r"udyam\s+registration\s+certificate",
            r"ministry\s+of\s+micro,\s+small\s+and\s+medium\s+enterprises",
            r"udyam[- ]mh[- ]",
            r"udyam\s+no"
        ],
        "supporting": [
            r"enterprise\s+type",
            r"major\s+activity",
            r"date\s+of\s+incorporation",
            r"national\s+industry\s+classification"
        ],
        "negative": [],
        "weight": 10
    },

    "Agreement": {
        "required_any": [
            r"this\s+agreement",
            r"service\s+agreement",
            r"non[- ]disclosure\s+agreement",
            r"memorandum\s+of\s+understanding",
            r"commercial\s+agreement"
        ],
        "supporting": [
            r"party\s+of\s+the\s+first\s+part",
            r"witnesseth",
            r"terms\s+and\s+conditions",
            r"in\s+witness\s+whereof",
            r"jurisdiction"
        ],
        "negative": [],
        "weight": 8
    },

    "Prescription": {
        "required_any": [
            r"\brx\b",
            r"doctor'?s\s+prescription",
            r"medical\s+prescription",
            r"prescribed\s+medicines"
        ],
        "supporting": [
            r"dosage",
            r"tablet",
            r"capsule",
            r"diagnosis",
            r"mci\s+reg",
            r"consultant\s+physician"
        ],
        "negative": [
            r"marksheet"
        ],
        "weight": 8
    },

    "Discharge Summary": {
        "required_any": [
            r"discharge\s+summary",
            r"discharge\s+card",
            r"clinical\s+summary",
            r"patient\s+discharge"
        ],
        "supporting": [
            r"date\s+of\s+admission",
            r"date\s+of\s+discharge",
            r"diagnosis",
            r"hospital",
            r"condition\s+at\s+discharge"
        ],
        "negative": [],
        "weight": 9
    }
}

class ClassificationRules:
    """
    Deterministic, explainable, multi-signal document identification rule engine.
    Combines OCR evidence, layout headings, authority vocabulary, identifier patterns, and filename cues.
    """

    @classmethod
    def identify_document(cls, ocr_text: str, file_path: str = None, qr_data: str = None) -> Tuple[str, str, float, Dict[str, Any]]:
        """
        Evaluates extracted document text, structure, QR metadata, and filename to return:
        (canonical_doc_type, category, confidence_score, evidence_details)
        Uses deterministic, explainable multi-signal weighted scoring.
        """
        text = (ocr_text or "").lower()
        fname = os.path.basename(file_path or "").lower().replace("_", " ").replace("-", " ")
        qr_text = (qr_data or "").lower()

        # Normalize text by removing non-alphanumeric clutter
        clean_text = re.sub(r'[\r\t\f\v]+', ' ', text)
        clean_text = re.sub(r' +', ' ', clean_text).strip()

        combined_content = f"{clean_text}\n{qr_text}".strip()
        has_content = len(combined_content) >= 15

        scores: Dict[str, float] = {}
        evidence_matches: Dict[str, list] = {}

        # Evaluate all canonical document rules
        for doc_type, rule in DOCUMENT_EVIDENCE_RULES.items():
            score = 0.0
            matched_items = []
            req_matched = False

            # A. Check required/primary title patterns in actual document text (+8.0 pts)
            for pat in rule.get("required_any", []):
                if re.search(pat, combined_content, re.IGNORECASE):
                    score += 8.0
                    req_matched = True
                    matched_items.append(f"title_pattern:{pat}")
                    break

            # B. Check supporting keywords/patterns (+1.5 pts each, max 5 = 7.5 pts)
            sup_count = 0
            for pat in rule.get("supporting", []):
                if re.search(pat, combined_content, re.IGNORECASE):
                    score += 1.5
                    sup_count += 1
                    matched_items.append(f"supporting:{pat}")
                    if sup_count >= 5:
                        break

            # C. Check negative patterns (-8.0 pts)
            for pat in rule.get("negative", []):
                if re.search(pat, clean_text, re.IGNORECASE):
                    score -= 8.0
                    matched_items.append(f"negative_penalty:{pat}")

            # D. Supporting filename cue (+2.0 pts ONLY if primary title matched in document content)
            if req_matched and doc_type.lower() in fname:
                score += 2.0
                matched_items.append("filename_corroboration")

            if req_matched and score > 0:
                scores[doc_type] = score
                evidence_matches[doc_type] = matched_items

        # Build candidate rankings
        sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        candidate_list = [
            {"type": dt, "score": round(sc, 1), "category": DOCUMENT_CATEGORIES.get(dt, "General")}
            for dt, sc in sorted_candidates[:5]
        ]

        # Detect conflicting signals across disparate categories
        conflicting_signals = False
        conflict_description = ""
        if len(sorted_candidates) >= 2:
            top_type, top_score = sorted_candidates[0]
            second_type, second_score = sorted_candidates[1]
            top_cat = DOCUMENT_CATEGORIES.get(top_type, "")
            second_cat = DOCUMENT_CATEGORIES.get(second_type, "")
            if top_cat != second_cat and second_score >= 8.0 and abs(top_score - second_score) <= 2.5:
                conflicting_signals = True
                conflict_description = f"Ambiguous signals detected between {top_type} ({top_cat}) and {second_type} ({second_cat})"

        if sorted_candidates and not conflicting_signals:
            best_type, best_score = sorted_candidates[0]

            if best_score >= 8.0:
                # Strong multi-signal match: calibrate 78.0% to 98.0%
                conf = min(98.5, max(78.0, 72.0 + best_score * 1.8))
                cat = DOCUMENT_CATEGORIES.get(best_type, "General")

                return best_type, cat, round(conf, 1), {
                    "method": "weighted_multi_signal_matching",
                    "score": best_score,
                    "evidence": evidence_matches.get(best_type, []),
                    "category": cat,
                    "conflicting_signals": False,
                    "candidates": candidate_list
                }
            elif best_score >= 5.0:
                # Moderate partial match
                conf = min(77.0, max(55.0, 48.0 + best_score * 3.0))
                cat = DOCUMENT_CATEGORIES.get(best_type, "General")

                return best_type, cat, round(conf, 1), {
                    "method": "partial_multi_signal_matching",
                    "score": best_score,
                    "evidence": evidence_matches.get(best_type, []),
                    "category": cat,
                    "conflicting_signals": False,
                    "candidates": candidate_list
                }

        # Safe Guardrail: Unknown Document (NEVER guess, NEVER label as forged)
        # Calculate defensible low confidence score reflecting lack of evidence (e.g. 5% to 25%, not fixed 50%)
        highest_raw_score = sorted_candidates[0][1] if sorted_candidates else 0.0
        calculated_unknown_conf = round(max(5.0, min(30.0, highest_raw_score * 2.5)), 1)
        if not has_content:
            calculated_unknown_conf = 0.0

        reason_str = "Document vocabulary, layout, and structural patterns did not match any standard registered academic, identity, or government profile."
        if conflicting_signals:
            reason_str = conflict_description

        return "Unknown Document", "Unknown", calculated_unknown_conf, {
            "method": "insufficient_evidence",
            "reason": reason_str,
            "conflicting_signals": conflicting_signals,
            "score": highest_raw_score,
            "candidates": candidate_list
        }
