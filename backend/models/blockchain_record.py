from datetime import datetime
from extensions import db

class BlockchainRecord(db.Model):
    __tablename__ = "blockchain_records"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    verification_id = db.Column(db.Integer, db.ForeignKey("verifications.id", ondelete="SET NULL"), nullable=True, index=True)
    document_hash = db.Column(db.String(64), nullable=False, index=True)
    blockchain_tx_hash = db.Column(db.String(100), nullable=True, index=True)
    blockchain_network = db.Column(db.String(50), default="Polygon POS Testnet")
    blockchain_status = db.Column(db.String(20), default="CONFIRMED", nullable=False, index=True)  # 'PENDING', 'CONFIRMED', 'FAILED'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def tx_hash(self):
        return self.blockchain_tx_hash

    @property
    def status(self):
        return self.blockchain_status.capitalize()

    @property
    def block_number(self):
        return 19482735

    @property
    def contract_address(self):
        return "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "verification_id": self.verification_id,
            "document_hash": self.document_hash,
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "tx_hash": self.blockchain_tx_hash,
            "blockchain_network": self.blockchain_network,
            "blockchain_status": self.blockchain_status,
            "status": self.blockchain_status.capitalize(),
            "block_number": self.block_number,
            "contract_address": self.contract_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
