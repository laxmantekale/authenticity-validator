# Authentication Validator - REST API Documentation

## Overview
All endpoints accept and return `application/json` unless handling multipart file uploads (`multipart/form-data`) or binary report downloads (`application/pdf`).

**Base URL**: `http://localhost:5000`

---

## 1. System Health & Root

### `GET /`
Returns basic service info.
```json
{
  "status": "ok",
  "message": "Authentication Validator API is running",
  "version": "1.0.0"
}
```

### `GET /api/health`
Returns system status, active database backend, and AI engine status.
```json
{
  "status": "ok",
  "message": "Backend service is healthy",
  "database": "connected",
  "ai_engine": "ready",
  "timestamp": "2026-09-06T20:00:00Z"
}
```

---

## 2. Authentication API (`/api/auth`)

### `POST /api/auth/register`
Registers a new Student or College account.
- **Request Body**:
```json
{
  "email": "student@example.edu",
  "password": "SecurePassword123!",
  "role": "student", // "student" or "college"
  "name": "Jane Doe",
  "college_id": 1, // optional for student
  "registration_no": "REG2026001" // optional
}
```
- **Response** (`201 Created`):
```json
{
  "success": true,
  "message": "Registration successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "user": {
    "id": 1,
    "email": "student@example.edu",
    "role": "student",
    "name": "Jane Doe"
  }
}
```

### `POST /api/auth/login`
Authenticates credentials and returns a signed JWT.
- **Request Body**:
```json
{
  "email": "student@example.edu",
  "password": "SecurePassword123!"
}
```
- **Response** (`200 OK`):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "user": {
    "id": 1,
    "email": "student@example.edu",
    "role": "student",
    "name": "Jane Doe"
  }
}
```

### `GET /api/auth/me`
Fetches currently authenticated user identity.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`

---

## 3. Student Operations (`/api/student`)
*All require `Authorization: Bearer <TOKEN>` with role `student`.*

- `GET /api/student/profile`: Fetch student profile details.
- `PUT /api/student/profile`: Update contact info and department.
- `GET /api/student/colleges`: List all linked / enrolled colleges with approval statuses.
- `GET /api/student/documents`: Fetch all student-uploaded documents.
- `GET /api/student/history`: Fetch complete historical verification records.
- `GET /api/student/reports`: Fetch generated authenticity audit reports.

---

## 4. College Operations (`/api/college`)
*All require `Authorization: Bearer <TOKEN>` with role `college`.*

- `GET /api/college/profile`: Fetch college institutional profile.
- `PUT /api/college/profile`: Update college name, accreditation, address.
- `GET /api/college/qr`: Returns college dynamic verification QR code payload & image URL.
- `GET /api/college/students`: List all linked and pending student enrollment applications.
- `POST /api/college/students/approve`: Approve or reject student enrollment request.
  ```json
  { "link_id": 4, "action": "approved" }
  ```
- `GET /api/college/documents`: View all documents issued or verified by this college.
- `GET /api/college/history`: Institutional verification logs.
- `GET /api/college/reports`: Generated institutional audit reports.

---

## 5. College Linking & QR Management (`/api/college-link`)

- `POST /api/college-link/scan`: Process college QR code scan from student device.
  - *Note*: Does not auto-link student; creates a pending linkage request awaiting college confirmation.
- `POST /api/college-link/request`: Student requests affiliation with target college ID.
- `GET /api/college-link/requests`: Fetch pending linkage requests for a college.
- `POST /api/college-link/respond`: College approves or rejects connection.

---

## 6. Document Verification & AI Engine (`/api/verification` & `/api/documents`)

### `POST /api/documents/upload`
Uploads a document file (`multipart/form-data`) with field `file` and document metadata.
- **Response**:
```json
{
  "success": true,
  "document_id": 12,
  "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "filename": "degree_certificate.pdf",
  "url": "/uploads/documents/degree_certificate.pdf"
}
```

### `POST /api/verification/verify`
Runs the multi-stage AI, database, and blockchain verification pipeline.
- **Request Body**:
```json
{
  "document_id": 12,
  "student_id": 1,
  "college_id": 2,
  "enable_ai": true,
  "enable_blockchain": true
}
```
- **Response**:
```json
{
  "success": true,
  "verification_id": 8,
  "status": "VERIFIED",
  "confidence_score": 0.982,
  "ai_analysis": {
    "classification": { "predicted_class": "Degree_Certificate", "confidence": 0.994 },
    "forgery_detection": { "is_forged": false, "tamper_score": 0.012 },
    "signature_verification": { "signature_matched": true, "similarity": 0.96 }
  },
  "blockchain": {
    "tx_hash": "0x4b72...a931",
    "block_number": 10429,
    "contract_verified": true
  },
  "report_id": 5
}
```

---

## 7. Reports & Blockchain Verification (`/api/reports` & `/api/blockchain`)

- `GET /api/reports/download/:id`: Download compiled PDF audit certificate.
- `GET /api/blockchain/verify/:hash`: Public lookup for SHA-256 hash on smart contract.
- `GET /api/blockchain/status`: Returns current network connection status and smart contract address.
