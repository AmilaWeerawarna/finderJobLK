from flask import Blueprint, request, session, jsonify
from src.repositories.wishlist_repository import WishlistRepository

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route("/wishlist/toggle", methods=["POST"])
def toggle_wishlist():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    job_id = data.get("job_id")
    score = data.get("score", 0)  
    
    repo = WishlistRepository()
    
    if repo.is_job_wishlisted(user_id, job_id):
        repo.remove_from_wishlist(user_id, job_id)
        return jsonify({"status": "removed", "message": "Removed from Wishlist"})
    else:
        repo.add_to_wishlist(user_id, job_id, score) 
        return jsonify({"status": "added", "message": "Added to Wishlist"})