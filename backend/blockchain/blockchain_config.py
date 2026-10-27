import os
import json

BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
WALLET_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY", None)
ENABLE_REAL_BLOCKCHAIN = os.getenv("ENABLE_REAL_BLOCKCHAIN", "false").lower() == "true"

def get_contract_abi():
    abi_path = os.path.join(os.path.dirname(__file__), "abi", "AuthenticityValidator.json")
    if os.path.exists(abi_path):
        with open(abi_path, "r") as f:
            return json.load(f)
    return []
