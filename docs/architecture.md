# Authentication Validator - System Architecture

## Overview
The **Authentication Validator** is an enterprise-grade document authenticity and tamper-detection platform engineered for educational institutions, universities, credential verification bodies, and students. It combines **Deep Learning (Computer Vision / NLP)**, **Blockchain immutability**, and **Cryptographic digital signatures** with secure QR code verification to combat academic credential fraud.

---

## High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client Layer [Frontend - React 18 / Vite / TailwindCSS]
        SP[Student Portal]
        CP[College Portal]
        PublicV[Public Verification Portal / QR Scanner]
        RAuth[AuthContext & Protected Routes]
    end

    subgraph API Gateway / Server Layer [Backend - Python Flask REST API]
        CORS[CORS & Security Middleware]
        JWT[JWT Authentication & RBAC]
        Routes[API Routes: Auth, Student, College, Verification, Documents, Reports, Blockchain]
        Services[Service Layer: DocumentService, VerificationService, BlockchainService, ReportService]
    end

    subgraph AI Intelligence Layer [AI / Deep Learning Engines]
        DocClass[Document Classifier: EfficientNet / CNN - 10 Classes]
        ForgDet[Forgery & Tamper Detection: Dual-Stream ELA + Feature CNN]
        SigVer[Signature Authenticity: Siamese / Triplet Network]
        Fallback[Graceful Fallback Mode]
    end

    subgraph Ledger & Storage Layer [Data & Trust Layer]
        SQL[(Relational Database: SQLite / MySQL)]
        BC[Blockchain Smart Contract: Ethereum / Polygon / Ganache]
        FS[Secure File Storage: Uploads & Verification Reports]
    end

    Client Layer -->|REST API & JWT| API Gateway / Server Layer
    API Gateway / Server Layer --> AI Intelligence Layer
    API Gateway / Server Layer --> SQL
    API Gateway / Server Layer --> BC
    API Gateway / Server Layer --> FS
```

---

## Core Subsystems

### 1. Client Layer (Frontend)
- **Framework**: React 18 with Vite, React Router DOM v6, Tailwind CSS, Lucide React icons, Axios, and html5-qrcode.
- **Portals**:
  - **Student Portal**: Document upload, verification tracking, enrolled colleges, digital certificates, verification history, and downloadable authenticity reports.
  - **College Portal**: Institutional QR generation, student enrollment review/approval, batch document issuance, institutional verification history, and analytics.
  - **Public Verification**: Zero-login QR scan or file hash lookup to instantly verify academic records against blockchain records.

### 2. Service & Business Logic Layer (Backend)
- **Framework**: Python 3.10+ with Flask, SQLAlchemy, PyJWT, ReportLab, OpenCV, and Web3.py.
- **Service Layer Pattern**: Decouples API endpoints from database models and external integrations.
  - `AuthService`: Password hashing (bcrypt/PBKDF2), JWT token creation, identity validation.
  - `DocumentService`: File validation, MIME checking, SHA-256 integrity hashing, and storage.
  - `VerificationService`: Multi-stage verification pipeline orchestrating OCR, AI models, and database comparisons.
  - `BlockchainService`: Web3 contract interaction, transaction creation, event logs, and on-chain hash verification.
  - `ReportService`: Dynamic PDF report compilation with cryptographic verification badges and audit QR codes.

### 3. AI Intelligence Engine
- **Document Classification**: Predicts document category (Degree, Transcript, Marksheet, Bonafide, etc.) with confidence scoring.
- **Forgery Detection**: Error Level Analysis (ELA) and texture frequency analysis to detect cloned stamps, modified numbers, font inconsistencies, and splicing.
- **Signature Verification**: Signature extraction and similarity comparison against institutional reference records.
- **Resilience**: Implements graceful degradation (`AI model unavailable - Development verification mode`) if GPU or model weights are temporarily inaccessible.

### 4. Blockchain & Trust Layer
- **Smart Contract (`AuthenticityValidator.sol`)**:
  - Immutably registers document SHA-256 hashes, student identifiers, issuing college addresses, and timestamps.
  - Emits `DocumentRegistered` and `DocumentVerified` events.
  - Prevents double-registration and post-issuance tampering.

---

## Security Architecture
1. **Cryptographic Integrity**: Every document undergoes SHA-256 fingerprinting upon upload. Any 1-bit alteration invalidates the certificate.
2. **Role-Based Access Control (RBAC)**: Secure JWT authentication separating `student`, `college`, and `admin` scopes.
3. **Decentralized Verification**: Verifiers can directly check the SHA-256 hash on public blockchain explorers without accessing confidential student PII.
4. **Sanitized File Handlers**: File size limits, allowed extensions (`.pdf`, `.png`, `.jpg`, `.jpeg`), and secure filename generation prevent path traversal and arbitrary code execution.
