# Authentication Validator – Database Documentation

This directory contains the complete relational schema, demo seed script, and configuration instructions for the **Authentication Validator** MySQL database.

---

## Database Architecture Overview

Database Name: `authenticity_validator`  
Engine: `InnoDB`  
Default Charset: `utf8mb4`  
Collation: `utf8mb4_unicode_ci`

### Entity Relationship Model

```text
users
  ├── students
  │     ├── college_student_links ── colleges
  │     ├── documents
  │     │     ├── verifications
  │     │     │     ├── verification_history
  │     │     │     ├── reports
  │     │     │     └── blockchain_records
  │     │     └── blockchain_records
  │     └── reports
  └── colleges
```

---

## Table Definitions

| # | Table Name | Purpose | Primary Key | Foreign Keys / Key Constraints |
|---|------------|---------|-------------|--------------------------------|
| 1 | `users` | Core credentials and role (`STUDENT`, `COLLEGE`) | `id` | Unique `email` |
| 2 | `students` | Student profile info & unique `student_id` | `id` | `user_id` -> `users.id`, Unique `student_id` |
| 3 | `colleges` | College profile, code, unique QR and Link tokens | `id` | `user_id` -> `users.id`, Unique `college_id`, `qr_token`, `secure_link_token` |
| 4 | `college_student_links` | Manages link requests (`PENDING`, `ACCEPTED`, `REJECTED`) | `id` | `student_id` -> `students.id`, `college_id` -> `colleges.id`, Unique (`student_id`, `college_id`) |
| 5 | `documents` | Uploaded academic files, MIME type, SHA-256 hash | `id` | `student_id` -> `students.id`, `college_id` -> `colleges.id` (nullable) |
| 6 | `verifications` | 12-layer verification outcomes & final status | `id` | `document_id` -> `documents.id`, `student_id` -> `students.id`, Unique `verification_id` |
| 7 | `verification_history` | Permanent, non-deletable audit trail | `id` | `verification_id` -> `verifications.id`, `student_id` -> `students.id` |
| 8 | `reports` | Official ReportLab PDF metadata (`AVR-XXXXX`) | `id` | `verification_id` -> `verifications.id`, Unique `report_id` |
| 9 | `blockchain_records` | On-chain SHA-256 hash and transaction reference | `id` | `document_id` -> `documents.id`, `verification_id` -> `verifications.id` |

---

## Step-by-Step MySQL Setup Guide

### Step 1: Create Database & Tables

Log in to MySQL via command line or MySQL Workbench:

```bash
mysql -u root -p < database/schema.sql
```

Or from inside MySQL client:

```sql
SOURCE database/schema.sql;
```

### Step 2: Load Seed Data

```bash
mysql -u root -p < database/seed.sql
```

Or from inside MySQL client:

```sql
SOURCE database/seed.sql;
```

### Step 3: Configure Backend `.env`

Copy `backend/.env.example` to `backend/.env` and provide your MySQL credentials:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/authenticity_validator
DB_HOST=localhost
DB_PORT=3306
DB_NAME=authenticity_validator
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
```

---

## Demo Accounts in Seed Data

| Role | Name / Institution | Email | Password | Code | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **COLLEGE** | National Institute of Technology (NIT) | `admin@nit.edu.in` | `Password@123` | `NIT101` | Active |
| **COLLEGE** | Metropolitan University of Tech (MUT) | `registrar@mut.edu.in` | `Password@123` | `MUT202` | Active |
| **STUDENT** | Rahul Patil | `rahul.patil@student.in` | `Password@123` | `STU001` | Linked to NIT |
| **STUDENT** | Amit Jadhav | `amit.jadhav@student.in` | `Password@123` | `STU002` | Pending NIT |
| **STUDENT** | Priya Sharma | `priya.sharma@student.in` | `Password@123` | `STU003` | Linked to MUT |
| **STUDENT** | Sneha Kulkarni | `sneha.k@student.in` | `Password@123` | `STU004` | Rejected NIT |
| **STUDENT** | Rohan Mehta | `rohan.mehta@student.in` | `Password@123` | `STU005` | Independent |

---

## Troubleshooting MySQL Connection

1. **Access Denied / Authentication Plugin**:
   If encountering `auth_gssapi_client` or `caching_sha2_password` issues, ensure your user is configured for native or standard caching password:
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
   FLUSH PRIVILEGES;
   ```
2. **Port in use / Host unreachable**:
   Verify MySQL service is running on Windows Service Manager (`MySQL80`) on port `3306`.
3. **Fallback Mode**:
   The Flask backend automatically detects if MySQL is accessible and gracefully falls back to the persistent SQLite database `authenticity_validator.db` if MySQL server credentials are not yet configured in `.env`.
