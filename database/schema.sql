-- ==========================================================
-- Authentication Validator
-- Relational MySQL Schema Definition
-- ==========================================================

CREATE DATABASE IF NOT EXISTS authenticity_validator
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE authenticity_validator;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'COLLEGE') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(191) NOT NULL,
    mobile VARCHAR(25) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_code (student_id),
    INDEX idx_student_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. COLLEGES TABLE
CREATE TABLE IF NOT EXISTS colleges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    college_id VARCHAR(50) NOT NULL UNIQUE,
    college_name VARCHAR(255) NOT NULL,
    official_email VARCHAR(191) NOT NULL,
    mobile VARCHAR(25) NOT NULL,
    address TEXT NOT NULL,
    qr_token VARCHAR(100) NOT NULL UNIQUE,
    secure_link_token VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_college_code (college_id),
    INDEX idx_college_qr (qr_token),
    INDEX idx_college_link (secure_link_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. COLLEGE STUDENT LINKS TABLE
CREATE TABLE IF NOT EXISTS college_student_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    college_id INT NOT NULL,
    status ENUM('PENDING', 'ACCEPTED', 'REJECTED', 'UNLINKED', 'REMOVED') DEFAULT 'PENDING' NOT NULL,
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    accepted_at DATETIME NULL,
    rejected_at DATETIME NULL,
    unlinked_at DATETIME NULL,
    unlinked_by ENUM('STUDENT', 'COLLEGE') NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_college (student_id, college_id),
    INDEX idx_link_status (status),
    INDEX idx_link_student (student_id),
    INDEX idx_link_college (college_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NULL,
    college_id INT NULL,
    document_type VARCHAR(100) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size INT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    deleted_at DATETIME NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    INDEX idx_doc_hash (file_hash),
    INDEX idx_doc_student (student_id),
    INDEX idx_doc_college (college_id),
    INDEX idx_doc_type (document_type),
    INDEX idx_doc_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. VERIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    student_id INT NULL,
    college_id INT NULL,
    verification_source VARCHAR(20) DEFAULT 'STUDENT' NOT NULL,
    final_status VARCHAR(30) NOT NULL,
    ocr_status VARCHAR(50) DEFAULT 'PASSED',
    qr_status VARCHAR(50) DEFAULT 'NOT_APPLICABLE',
    forgery_status VARCHAR(50) DEFAULT 'PASSED',
    signature_status VARCHAR(50) DEFAULT 'NOT_APPLICABLE',
    stamp_status VARCHAR(50) DEFAULT 'NOT_APPLICABLE',
    metadata_status VARCHAR(50) DEFAULT 'PASSED',
    database_status VARCHAR(50) DEFAULT 'NOT_APPLICABLE',
    confidence_score FLOAT DEFAULT 0.95,
    verification_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    verification_id VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    INDEX idx_ver_source (verification_source),
    INDEX idx_ver_final_status (final_status),
    INDEX idx_ver_date (verification_date),
    INDEX idx_ver_id (verification_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. VERIFICATION HISTORY TABLE
CREATE TABLE IF NOT EXISTS verification_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    verification_id INT NOT NULL,
    student_id INT NULL,
    college_id INT NULL,
    verification_source ENUM('STUDENT', 'COLLEGE') DEFAULT 'STUDENT' NOT NULL,
    document_id INT NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    authentication_status VARCHAR(50) NOT NULL,
    verification_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    report_id VARCHAR(50) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verification_id) REFERENCES verifications(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_hist_source (verification_source),
    INDEX idx_hist_student (student_id),
    INDEX idx_hist_college (college_id),
    INDEX idx_hist_ver (verification_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. REPORTS TABLE
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id VARCHAR(50) NOT NULL UNIQUE,
    verification_id INT NOT NULL,
    student_id INT NULL,
    college_id INT NULL,
    verification_source ENUM('STUDENT', 'COLLEGE') DEFAULT 'STUDENT' NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    authentication_status VARCHAR(50) NOT NULL,
    report_file_path VARCHAR(500) NOT NULL,
    report_data LONGTEXT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verification_id) REFERENCES verifications(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL,
    INDEX idx_rep_id (report_id),
    INDEX idx_rep_source (verification_source),
    INDEX idx_rep_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. BLOCKCHAIN RECORDS TABLE
CREATE TABLE IF NOT EXISTS blockchain_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    verification_id INT NOT NULL,
    document_hash VARCHAR(64) NOT NULL,
    blockchain_tx_hash VARCHAR(100) NULL,
    blockchain_network VARCHAR(50) DEFAULT 'Polygon POS Testnet',
    blockchain_status ENUM('PENDING', 'CONFIRMED', 'FAILED') DEFAULT 'CONFIRMED' NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (verification_id) REFERENCES verifications(id) ON DELETE CASCADE,
    INDEX idx_bc_hash (document_hash),
    INDEX idx_bc_tx (blockchain_tx_hash),
    INDEX idx_bc_status (blockchain_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. PASSWORD RESET TOKENS TABLE
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token_hash (token_hash),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_pwd_reset_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

