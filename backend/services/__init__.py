from services.auth_service import AuthService
from services.student_service import StudentService
from services.college_service import CollegeService
from services.college_link_service import CollegeLinkService
from services.document_service import DocumentService
from services.verification_service import VerificationService
from services.history_service import HistoryService
from services.report_service import ReportService, report_service
from services.blockchain_service import BlockchainService

__all__ = [
    "AuthService",
    "StudentService",
    "CollegeService",
    "CollegeLinkService",
    "DocumentService",
    "VerificationService",
    "HistoryService",
    "ReportService",
    "report_service",
    "BlockchainService"
]
