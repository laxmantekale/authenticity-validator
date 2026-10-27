# Authentication Validator

Secure Academic Document Verification Platform

An enterprise-grade, full-stack document authenticity and tamper-detection platform engineered for educational institutions, universities, credential verification bodies, and students. The platform leverages **Deep Learning (Computer Vision & NLP)**, **Ethereum/Polygon Smart Contracts**, and **Cryptographic digital signatures** with secure QR verification to combat academic credential fraud.

---

## 🚀 Key Features

1. **Dual Portal Architecture**:
   - **Student Portal**: Independent account creation, document upload & verification tracking, college linking via QR Scan / Directory / Links, digital credential wallet, non-deletable verification history, and official PDF authenticity reports.
   - **College / Institute Portal**: Custom institutional QR generator, student enrollment verification console (approve/reject workflow), institutional document repository, historical verification logs, and audit reports.
2. **AI & Deep Learning Verification Suite**:
   - **Document Classifier (Keras)**: Classifies academic documents across 10 classes (10th/12th Marksheet, Diploma, Degree, Leaving/Transfer, Bonafide, Caste, Income, Domicile, Scholarship) with confidence scoring.
   - **Forgery Detection Model (Keras)**: Dual-stream Error Level Analysis (ELA) and texture frequency analysis to detect cloned stamps, modified text, font inconsistencies, and splicing.
   - **Signature Authenticity Model (Keras)**: Signature extraction and similarity comparison against institutional reference records.
   - **Graceful Degradation**: Fallback to development verification mode if AI models or GPU weights are temporarily unavailable.
3. **Decentralized Blockchain Trust Layer**:
   - **Smart Contract (`AuthenticityValidator.sol`)**: Immutably registers SHA-256 document fingerprints, issuing college addresses, and timestamps on Ethereum / Polygon / Ganache.
   - **Zero-Downtime Web3 Service**: Seamlessly bridges on-chain smart contracts with backend transaction logging.
4. **Official ReportLab PDF Reports (`AVR-XXXXX`)**:
   - High-resolution audit certificates containing student metadata, verification status, cryptographic SHA-256 seal, and verifiable QR checksum.
5. **Multi-Database Support**:
   - Production **MySQL 8.0+** schema with SQLite automatic zero-config fallback.

---

## 📁 Project Structure

```text
authenticity-validator/
├── backend/
│   ├── ai/
│   │   ├── models/                    # Trained .keras models
│   │   │   ├── document_classifier.keras
│   │   │   ├── forgery_model.keras
│   │   │   └── signature_model.keras
│   │   ├── preprocessing/             # Image & document preprocessing pipelines
│   │   ├── training/                  # Model training scripts & metric reports
│   │   ├── classification_inference.py
│   │   ├── forgery_inference.py
│   │   └── signature_inference.py
│   ├── blockchain/
│   │   ├── contracts/                 # AuthenticityValidator.sol
│   │   ├── abi/                       # AuthenticityValidator.json
│   │   ├── blockchain_config.py
│   │   └── blockchain_service.py
│   ├── controllers/ / services/       # Service layer
│   ├── models/                        # SQLAlchemy database models
│   ├── routes/                        # Flask Blueprints
│   ├── utils/                         # Cryptography, security, QR & PDF utils
│   ├── uploads/                       # Document storage & generated PDF reports
│   ├── app.py                         # Flask entrypoint (Port 5000)
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                # Modular React components
│   │   │   ├── auth/                  # LoginForm, RegisterForm
│   │   │   ├── common/                # Loader, ProtectedRoute
│   │   │   ├── documents/             # DocumentCard, DocumentPreview, DocumentUploader
│   │   │   ├── qr/                    # QRScanner, QRGenerator, CollegeQRCard
│   │   │   ├── reports/               # ReportCard, ReportViewer
│   │   │   └── verification/          # VerificationProgress, VerificationResult
│   │   ├── pages/                     # Student & College portal views
│   │   ├── services/                  # Modular Axios API services
│   │   ├── context/                   # AuthContext
│   │   ├── hooks/                     # Custom React hooks (useAuth)
│   │   ├── utils/                     # Validators, constants
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
├── database/
│   ├── schema.sql                     # Relational MySQL DDL
│   ├── seed.sql                       # Seed data
│   └── README.md
├── datasets/                          # Training datasets
├── docs/                              # Architecture, API & Blockchain design docs
├── docker-compose.yml                 # Full-stack Docker orchestration
└── README.md
```

---

## 🛠️ Setup & Installation

### Option 1: Full-Stack Docker Compose

Run the entire stack (MySQL 8.0, Flask Backend, and React Vite Frontend) with one command:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80`
- Backend API: `http://localhost:5000`
- MySQL: `localhost:3306`

---

### Option 2: Local Manual Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. AI Model Training (Optional - Pretrained models included)
```bash
# Generate synthetic development training datasets
python ai/create_dev_datasets.py

# Train the 3 AI models
python ai/training/train_classifier.py
python ai/training/train_forgery.py
python ai/training/train_signature.py
```

#### 3. Database Configuration
By default, the backend runs on persistent SQLite with zero configuration. To use MySQL:
1. Import `database/schema.sql` and `database/seed.sql` into MySQL Server.
2. In `backend/.env`, set:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/authenticity_validator
```

#### 4. Run the Flask Backend
```bash
python app.py
```
*Backend runs on `http://127.0.0.1:5000`.*

#### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## 🧪 Testing & Verification

Run the comprehensive end-to-end integration test suite:
```bash
python test_complete_frontend_flow.py
```
To build the frontend for production:
```bash
cd frontend
npm run build
```

---

## 🔐 Demo Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **College (NIT)** | `admin@nit.edu.in` | `Password@123` | Institutional Admin & QR Manager |
| **College (MUT)** | `registrar@mut.edu.in` | `Password@123` | Institutional Admin |
| **Student (Rahul Patil)** | `rahul.patil@student.in` | `Password@123` | Enrolled / Linked Student |
| **Student (Amit Jadhav)** | `amit.jadhav@student.in` | `Password@123` | Pending College Approval |
| **Student (Rohan Mehta)** | `rohan.mehta@student.in` | `Password@123` | Independent Student |
