import os
import uuid
from datetime import datetime
from blockchain.blockchain_service import BlockchainService as CoreBlockchainService

class BlockchainService:
    @staticmethod
    def anchor_document(doc_hash, student_ref, college_ref, doc_type, overall_status):
        core = CoreBlockchainService()
        return core.anchor_document(
            doc_hash=doc_hash,
            student_ref=student_ref,
            college_ref=college_ref,
            doc_type=doc_type,
            overall_status=overall_status
        )

    @staticmethod
    def get_document_record(doc_hash):
        from models.blockchain_record import BlockchainRecord
        record = BlockchainRecord.query.filter_by(document_hash=doc_hash).first()
        return record.to_dict() if record else None
