-- ==========================================================
-- Authentication Validator
-- Safe Demo Data Seeder (DEMO ONLY)
-- ==========================================================

USE authenticity_validator;

-- Clean existing demo data safely
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE blockchain_records;
TRUNCATE TABLE reports;
TRUNCATE TABLE verification_history;
TRUNCATE TABLE verifications;
TRUNCATE TABLE documents;
TRUNCATE TABLE college_student_links;
TRUNCATE TABLE colleges;
TRUNCATE TABLE students;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. USERS (bcrypt hash for 'Password@123': $2b$12$K1r.Jc37zW/m1qWv8w1R3.7s5Q2h7yH7sL1iV5iQ8j0iP9yZ1x.Nu)
INSERT INTO users (id, email, password_hash, role, created_at, updated_at) VALUES
(1, 'admin@nit.edu.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'COLLEGE', NOW(), NOW()),
(2, 'registrar@mut.edu.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'COLLEGE', NOW(), NOW()),
(3, 'rahul.patil@student.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'STUDENT', NOW(), NOW()),
(4, 'amit.jadhav@student.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'STUDENT', NOW(), NOW()),
(5, 'priya.sharma@student.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'STUDENT', NOW(), NOW()),
(6, 'sneha.k@student.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'STUDENT', NOW(), NOW()),
(7, 'rohan.mehta@student.in', '$2b$12$w0J/WcRjNq2z1e6n9Hw37uL4n4g7e1b5b2k8t9q1o2p3r4s5t6u7v', 'STUDENT', NOW(), NOW());

-- 2. COLLEGES
INSERT INTO colleges (id, user_id, college_id, college_name, official_email, mobile, address, qr_token, secure_link_token, created_at, updated_at) VALUES
(1, 1, 'NIT101', 'National Institute of Technology (NIT)', 'admin@nit.edu.in', '+91 9123456780', 'NIT Campus, Tech Park Road, Bangalore, Karnataka - 560001', 'qr_token_nit101_demo_sec_99a', 'sec_link_nit101_demo', NOW(), NOW()),
(2, 2, 'MUT202', 'Metropolitan University of Technology (MUT)', 'registrar@mut.edu.in', '+91 9123456781', 'MUT Towers, Knowledge City, New Delhi - 110001', 'qr_token_mut202_demo_sec_88b', 'sec_link_mut202_demo', NOW(), NOW());

-- 3. STUDENTS
INSERT INTO students (id, user_id, student_id, full_name, mobile, created_at, updated_at) VALUES
(1, 3, 'STU001', 'Rahul Patil', '+91 9123456701', NOW(), NOW()),
(2, 4, 'STU002', 'Amit Jadhav', '+91 9123456702', NOW(), NOW()),
(3, 5, 'STU003', 'Priya Sharma', '+91 9123456703', NOW(), NOW()),
(4, 6, 'STU004', 'Sneha Kulkarni', '+91 9123456704', NOW(), NOW()),
(5, 7, 'STU005', 'Rohan Mehta', '+91 9123456705', NOW(), NOW());

-- 4. COLLEGE STUDENT LINKS
INSERT INTO college_student_links (id, student_id, college_id, status, requested_at, accepted_at, rejected_at, created_at, updated_at) VALUES
(1, 1, 1, 'ACCEPTED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY), NULL, NOW(), NOW()),
(2, 1, 2, 'PENDING', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL, NULL, NOW(), NOW()),
(3, 2, 1, 'PENDING', DATE_SUB(NOW(), INTERVAL 2 DAY), NULL, NULL, NOW(), NOW()),
(4, 3, 2, 'ACCEPTED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY), NULL, NOW(), NOW()),
(5, 4, 1, 'REJECTED', DATE_SUB(NOW(), INTERVAL 10 DAY), NULL, DATE_SUB(NOW(), INTERVAL 9 DAY), NOW(), NOW());

-- 5. DOCUMENTS
INSERT INTO documents (id, student_id, college_id, document_type, original_filename, stored_filename, file_path, file_hash, file_size, mime_type, uploaded_at, created_at, updated_at) VALUES
(1, 1, 1, '10th Marksheet', '10th_Marksheet_STU001.pdf', 'demo_10th_Marksheet_STU001.pdf', 'uploads/demo_10th_Marksheet_STU001.pdf', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 45020, 'application/pdf', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW(), NOW()),
(2, 1, 1, '12th Marksheet', '12th_Marksheet_STU001.pdf', 'demo_12th_Marksheet_STU001.pdf', 'uploads/demo_12th_Marksheet_STU001.pdf', '8a5f3f4c6e2b1a9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c', 48910, 'application/pdf', DATE_SUB(NOW(), INTERVAL 4 DAY), NOW(), NOW()),
(3, 1, NULL, 'Caste Certificate', 'Caste_Certificate_STU001.pdf', 'demo_Caste_Certificate_STU001.pdf', 'uploads/demo_Caste_Certificate_STU001.pdf', '1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d', 38200, 'application/pdf', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW(), NOW()),
(4, 2, NULL, 'Degree Certificate', 'Degree_Certificate_STU002.pdf', 'demo_Degree_Certificate_STU002.pdf', 'uploads/demo_Degree_Certificate_STU002.pdf', '7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c', 51200, 'application/pdf', DATE_SUB(NOW(), INTERVAL 2 DAY), NOW(), NOW()),
(5, 3, 2, 'Income Certificate', 'Income_Certificate_STU003.pdf', 'demo_Income_Certificate_STU003.pdf', 'uploads/demo_Income_Certificate_STU003.pdf', '3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b', 34500, 'application/pdf', DATE_SUB(NOW(), INTERVAL 6 DAY), NOW(), NOW()),
(6, 5, NULL, 'Domicile Certificate', 'Domicile_Certificate_STU005.pdf', 'demo_Domicile_Certificate_STU005.pdf', 'uploads/demo_Domicile_Certificate_STU005.pdf', '5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a', 41000, 'application/pdf', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW(), NOW());

-- 6. VERIFICATIONS
INSERT INTO verifications (id, document_id, student_id, college_id, final_status, ocr_status, qr_status, forgery_status, signature_status, stamp_status, metadata_status, database_status, verification_date, verification_id, created_at) VALUES
(1, 1, 1, 1, 'AUTHENTICATED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', DATE_SUB(NOW(), INTERVAL 5 DAY), 'VER-00001', NOW()),
(2, 2, 1, 1, 'AUTHENTICATED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', DATE_SUB(NOW(), INTERVAL 4 DAY), 'VER-00002', NOW()),
(3, 3, 1, NULL, 'NOT_AUTHENTICATED', 'PASSED', 'NOT_APPLICABLE', 'FAILED', 'NOT_APPLICABLE', 'NOT_APPLICABLE', 'PASSED', 'NOT_APPLICABLE', DATE_SUB(NOW(), INTERVAL 3 DAY), 'VER-00003', NOW()),
(4, 4, 2, NULL, 'AUTHENTICATED', 'PASSED', 'NOT_APPLICABLE', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'NOT_APPLICABLE', DATE_SUB(NOW(), INTERVAL 2 DAY), 'VER-00004', NOW()),
(5, 5, 3, 2, 'AUTHENTICATED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', 'PASSED', DATE_SUB(NOW(), INTERVAL 6 DAY), 'VER-00005', NOW()),
(6, 6, 5, NULL, 'AUTHENTICATED', 'PASSED', 'NOT_APPLICABLE', 'PASSED', 'PASSED', 'NOT_APPLICABLE', 'PASSED', 'NOT_APPLICABLE', DATE_SUB(NOW(), INTERVAL 1 DAY), 'VER-00006', NOW());

-- 7. VERIFICATION HISTORY
INSERT INTO verification_history (id, verification_id, student_id, college_id, document_id, document_name, authentication_status, verification_date, report_id, created_at) VALUES
(1, 1, 1, 1, 1, 'Class 10th Secondary School Certificate', 'AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 5 DAY), 'RPT-00001', NOW()),
(2, 2, 1, 1, 2, 'Class 12th Higher Secondary Marksheet', 'AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 4 DAY), 'RPT-00002', NOW()),
(3, 3, 1, NULL, 3, 'State Caste Category Certificate', 'NOT_AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 3 DAY), 'RPT-00003', NOW()),
(4, 4, 2, NULL, 4, 'Bachelor of Technology Degree Certificate', 'AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 2 DAY), 'RPT-00004', NOW()),
(5, 5, 3, 2, 5, 'Annual Family Income Certificate', 'AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 6 DAY), 'RPT-00005', NOW()),
(6, 6, 5, NULL, 6, 'State Resident Domicile Certificate', 'AUTHENTICATED', DATE_SUB(NOW(), INTERVAL 1 DAY), 'RPT-00006', NOW());

-- 8. REPORTS
INSERT INTO reports (id, report_id, verification_id, student_id, college_id, document_name, authentication_status, report_file_path, generated_at, created_at) VALUES
(1, 'RPT-00001', 1, 1, 1, 'Class 10th Secondary School Certificate', 'AUTHENTICATED', 'reports/RPT-00001.pdf', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW()),
(2, 'RPT-00002', 2, 1, 1, 'Class 12th Higher Secondary Marksheet', 'AUTHENTICATED', 'reports/RPT-00002.pdf', DATE_SUB(NOW(), INTERVAL 4 DAY), NOW()),
(3, 'RPT-00003', 3, 1, NULL, 'State Caste Category Certificate', 'NOT_AUTHENTICATED', 'reports/RPT-00003.pdf', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW()),
(4, 'RPT-00004', 4, 2, NULL, 'Bachelor of Technology Degree Certificate', 'AUTHENTICATED', 'reports/RPT-00004.pdf', DATE_SUB(NOW(), INTERVAL 2 DAY), NOW()),
(5, 'RPT-00005', 5, 3, 2, 'Annual Family Income Certificate', 'AUTHENTICATED', 'reports/RPT-00005.pdf', DATE_SUB(NOW(), INTERVAL 6 DAY), NOW()),
(6, 'RPT-00006', 6, 5, NULL, 'State Resident Domicile Certificate', 'AUTHENTICATED', 'reports/RPT-00006.pdf', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW());

-- 9. BLOCKCHAIN RECORDS
INSERT INTO blockchain_records (id, document_id, verification_id, document_hash, blockchain_tx_hash, blockchain_network, blockchain_status, timestamp, created_at) VALUES
(1, 1, 1, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW()),
(2, 2, 2, '8a5f3f4c6e2b1a9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c', '0x8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 4 DAY), NOW()),
(3, 3, 3, '1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d', '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW()),
(4, 4, 4, '7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c', '0x6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 2 DAY), NOW()),
(5, 5, 5, '3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b', '0x5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 6 DAY), NOW()),
(6, 6, 6, '5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a', '0x4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b', 'Polygon POS Testnet', 'CONFIRMED', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW());
