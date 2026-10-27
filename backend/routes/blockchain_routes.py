from flask import Blueprint, request, jsonify
from extensions import db
from models.blockchain_record import BlockchainRecord
from blockchain.blockchain_service import blockchain_service

blockchain_bp = Blueprint("blockchain", __name__)

@blockchain_bp.route("/verify-hash/<doc_hash>", methods=["GET"])
def verify_hash_endpoint(doc_hash):
    record = BlockchainRecord.query.filter_by(document_hash=doc_hash).first()
    chain_info = blockchain_service.verify_on_chain(doc_hash)

    if not record and not chain_info.get("exists"):
        return jsonify({
            "exists": False,
            "message": "No blockchain record found for this cryptographic hash"
        }), 404

    return jsonify({
        "exists": True,
        "record": record.to_dict() if record else chain_info["record"]
    }), 200

@blockchain_bp.route("/records", methods=["GET"])
def get_blockchain_records():
    records = BlockchainRecord.query.order_by(BlockchainRecord.timestamp.desc()).limit(20).all()
    return jsonify({"records": [r.to_dict() for r in records]}), 200
