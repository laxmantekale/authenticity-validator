import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_database_uri():
    # Direct DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "").strip()
    if db_url:
        return db_url

    # Or construct from parameters
    db_user = os.getenv("DB_USER", "").strip()
    db_password = os.getenv("DB_PASSWORD", "").strip()
    db_host = os.getenv("DB_HOST", "localhost").strip()
    db_port = os.getenv("DB_PORT", "3306").strip()
    db_name = os.getenv("DB_NAME", "authenticity_validator").strip()

    if db_user and db_name and db_password:
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

    # Default fallback to persistent SQLite database
    return f"sqlite:///{os.path.join(BASE_DIR, 'authenticity_validator.db')}"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "authenticity-validator-secure-prod-key-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-super-secure-key-academic-validation-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True
    }
    
    # Upload and Report folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # Blockchain config
    BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
    BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
    BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    
    # QR code settings
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
