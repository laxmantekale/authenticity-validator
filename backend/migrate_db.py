import sys
from app import create_app
from extensions import db
from sqlalchemy import text

def run_migration():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # 1. documents table
            try:
                conn.execute(text("ALTER TABLE documents MODIFY student_id INT NULL;"))
                print("1. Modified documents.student_id to NULL")
            except Exception as e:
                print("1. documents note:", e)

            try:
                conn.execute(text("ALTER TABLE documents ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;"))
                print("1b. Added documents.is_deleted")
            except Exception as e:
                print("1b. documents is_deleted note:", e)

            try:
                conn.execute(text("ALTER TABLE documents ADD COLUMN deleted_at DATETIME NULL;"))
                print("1c. Added documents.deleted_at")
            except Exception as e:
                print("1c. documents deleted_at note:", e)

            # 2. verifications table
            try:
                conn.execute(text("ALTER TABLE verifications MODIFY student_id INT NULL;"))
                print("2. Modified verifications.student_id to NULL")
            except Exception as e:
                print("2. verifications student_id note:", e)

            try:
                conn.execute(text("ALTER TABLE verifications ADD COLUMN verification_source VARCHAR(20) DEFAULT 'STUDENT' NOT NULL;"))
                print("3. Added verifications.verification_source")
            except Exception as e:
                print("3. verifications verification_source note:", e)

            try:
                conn.execute(text("ALTER TABLE verifications ADD COLUMN confidence_score FLOAT DEFAULT 0.95;"))
                print("3b. Added verifications.confidence_score")
            except Exception as e:
                print("3b. verifications confidence_score note:", e)

            try:
                conn.execute(text("ALTER TABLE verifications MODIFY COLUMN final_status VARCHAR(30) NOT NULL;"))
                print("3c. Modified verifications.final_status to VARCHAR(30) NOT NULL")
            except Exception as e:
                print("3c. verifications final_status note:", e)

            # 3. verification_history table
            try:
                conn.execute(text("ALTER TABLE verification_history MODIFY student_id INT NULL;"))
                print("4. Modified verification_history.student_id to NULL")
            except Exception as e:
                print("4. verification_history student_id note:", e)

            try:
                conn.execute(text("ALTER TABLE verification_history ADD COLUMN verification_source VARCHAR(20) DEFAULT 'STUDENT' NOT NULL;"))
                print("5. Added verification_history.verification_source")
            except Exception as e:
                print("5. verification_history verification_source note:", e)

            # 4. reports table
            try:
                conn.execute(text("ALTER TABLE reports MODIFY student_id INT NULL;"))
                print("6. Modified reports.student_id to NULL")
            except Exception as e:
                print("6. reports student_id note:", e)

            # 5. college_student_links table
            try:
                conn.execute(text("ALTER TABLE college_student_links MODIFY status VARCHAR(20) DEFAULT 'PENDING' NOT NULL;"))
                print("8. Modified college_student_links.status to VARCHAR(20)")
            except Exception as e:
                print("8. college_student_links status note:", e)

            try:
                conn.execute(text("ALTER TABLE college_student_links ADD COLUMN unlinked_at DATETIME NULL;"))
                print("9. Added college_student_links.unlinked_at")
            except Exception as e:
                print("9. college_student_links unlinked_at note:", e)

            try:
                conn.execute(text("ALTER TABLE college_student_links ADD COLUMN unlinked_by VARCHAR(20) NULL;"))
                print("10. Added college_student_links.unlinked_by")
            except Exception as e:
                print("10. college_student_links unlinked_by note:", e)

            # 6. password_reset_tokens table
            try:
                conn.execute(text("""
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
                """))
                print("11. Created password_reset_tokens table if not exists")
            except Exception as e:
                print("11. password_reset_tokens note:", e)

            # 7. Add report_data column to reports table
            try:
                conn.execute(text("ALTER TABLE reports ADD COLUMN report_data LONGTEXT NULL;"))
                print("12. Added reports.report_data")
            except Exception as e:
                print("12. reports report_data note:", e)

            conn.commit()
            print("Migration committed successfully!")

if __name__ == "__main__":
    run_migration()
