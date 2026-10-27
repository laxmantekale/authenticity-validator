# Authentication Validator - Database Design & Schema

## Database Architecture
The platform is designed to run seamlessly on both **MySQL 8.0+** (production enterprise grade) and **SQLite 3** (local developer zero-config mode) via SQLAlchemy ORM.

---

## Entity Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o| STUDENTS : "is student"
    USERS ||--o| COLLEGES : "is college"
    STUDENTS ||--o{ COLLEGE_STUDENT_LINKS : "requests enrollment"
    COLLEGES ||--o{ COLLEGE_STUDENT_LINKS : "approves / manages"
    STUDENTS ||--o{ DOCUMENTS : "owns"
    COLLEGES ||--o{ DOCUMENTS : "issues / approves"
    DOCUMENTS ||--o{ VERIFICATIONS : "evaluated in"
    VERIFICATIONS ||--|| REPORTS : "generates"
    VERIFICATIONS ||--o{ VERIFICATION_HISTORY : "logged in"
    VERIFICATIONS ||--o| BLOCKCHAIN_LOGS : "anchored to"

    USERS {
        int id PK
        string email UK
        string password_hash
        string role "student | college | admin"
        datetime created_at
        datetime updated_at
    }

    STUDENTS {
        int id PK
        int user_id FK
        string full_name
        string roll_number
        string department
        string phone
    }

    COLLEGES {
        int id PK
        int user_id FK
        string college_name
        string college_code UK
        string qr_code_identifier UK
        string address
        string contact_email
    }

    COLLEGE_STUDENT_LINKS {
        int id PK
        int student_id FK
        int college_id FK
        string status "pending | approved | rejected"
        datetime requested_at
        datetime responded_at
    }

    DOCUMENTS {
        int id PK
        int student_id FK
        int college_id FK
        string title
        string document_type
        string file_path
        string file_hash "SHA-256 UK"
        datetime uploaded_at
    }

    VERIFICATIONS {
        int id PK
        int document_id FK
        int verified_by FK
        string status "VERIFIED | REJECTED | PENDING"
        float confidence_score
        json ai_metrics
        string tx_hash
        datetime verified_at
    }

    VERIFICATION_HISTORY {
        int id PK
        int verification_id FK
        int student_id FK
        int college_id FK
        string action
        json details
        datetime timestamp
    }

    REPORTS {
        int id PK
        int verification_id FK
        string report_pdf_path
        string qr_verification_code
        datetime generated_at
    }

    BLOCKCHAIN_LOGS {
        int id PK
        int verification_id FK
        string document_hash
        string tx_hash
        int block_number
        datetime confirmed_at
    }
```

---

## Integrity & Preservation Rules
1. **Immutable History**: Historical verification logs (`VERIFICATION_HISTORY`) retain college and student snapshot IDs regardless of subsequent enrollment status updates or disaffiliations.
2. **Deterministic Document Fingerprint**: `DOCUMENTS.file_hash` is computed using raw binary SHA-256. If a duplicate hash is uploaded, the existing document record is referenced to prevent duplicate processing.
3. **Audit Trail**: Every verification result snapshot is preserved in `REPORTS` with an immutable PDF path and QR checksum.
