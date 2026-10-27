from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.history_service import HistoryService
from models.user import User

history_bp = Blueprint("history_routes", __name__, url_prefix="/api/history")

@history_bp.route("/student", methods=["GET"])
@jwt_required()
def get_student_history():
    user_id = int(get_jwt_identity())
    history = HistoryService.get_student_history(user_id)
    return jsonify({"history": history}), 200

@history_bp.route("/college", methods=["GET"])
@jwt_required()
def get_college_history():
    user_id = int(get_jwt_identity())
    history = HistoryService.get_college_history(user_id)
    return jsonify({"history": history}), 200
