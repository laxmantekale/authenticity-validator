from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.college_routes import college_bp
from routes.college_link_routes import college_link_bp
from routes.document_routes import document_bp
from routes.verification_routes import verification_bp
from routes.history_routes import history_bp
from routes.report_routes import report_bp
from routes.blockchain_routes import blockchain_bp

__all__ = [
    "auth_bp",
    "student_bp",
    "college_bp",
    "college_link_bp",
    "document_bp",
    "verification_bp",
    "history_bp",
    "report_bp",
    "blockchain_bp"
]
