from flask import Blueprint, request, session, jsonify
from src.repositories.history_repository import HistoryRepository

history_bp = Blueprint("history", __name__)

@history_bp.route("/history/remove", methods=["POST"])
def remove_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    job_id = data.get("job_id")
    
    repo = HistoryRepository()
    repo.remove_from_history(user_id, job_id)
    
    return jsonify({"status": "removed", "message": "Removed from History"})