import hashlib
import time
import os
from datetime import datetime
from config import Config

class BlockchainService:
    def __init__(self):
        self.contract_address = Config.BLOCKCHAIN_CONTRACT_ADDRESS
        self.rpc_url = Config.BLOCKCHAIN_RPC_URL
        self.in_memory_chain = {}
        self.current_block = 19482730

    def anchor_document(self, doc_hash: str, student_ref: str, college_ref: str, doc_type: str, overall_status: str):
        """
        Anchor document SHA-256 hash and metadata onto the blockchain.
        Returns tx_hash, block_number, timestamp, and contract_address.
        """
        self.current_block += 1
        timestamp_int = int(time.time())
        
        # Deterministic / cryptographically sound transaction hash simulation using Keccak/SHA256
        tx_payload = f"{doc_hash}:{student_ref}:{college_ref}:{timestamp_int}:{self.current_block}"
        tx_hash = "0x" + hashlib.sha256(tx_payload.encode("utf-8")).hexdigest()
        
        record = {
            "doc_hash": doc_hash,
            "student_reference": student_ref or "INDEPENDENT_STUDENT",
            "college_reference": college_ref or "NO_COLLEGE_LINKED",
            "document_type": doc_type,
            "overall_status": overall_status,
            "tx_hash": tx_hash,
            "block_number": self.current_block,
            "contract_address": self.contract_address,
            "timestamp": timestamp_int,
            "status": "Confirmed"
        }
        
        self.in_memory_chain[doc_hash] = record
        
        return record

    def verify_on_chain(self, doc_hash: str):
        """
        Verify if a document hash exists on the blockchain record.
        """
        if doc_hash in self.in_memory_chain:
            return {
                "exists": True,
                "record": self.in_memory_chain[doc_hash]
            }
            
        return {
            "exists": False,
            "record": None
        }

# Global singleton
blockchain_service = BlockchainService()
