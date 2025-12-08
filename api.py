from flask import Blueprint, jsonify, request, current_app
from models import Item, User
from extensions import db
from functools import wraps

bp = Blueprint("api", __name__)


# --- TOKEN AUTH DECORATOR ---
def token_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")

        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = header.split(" ", 1)[1]
        user = User.verify_api_token(token)

        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = user
        return f(*args, **kwargs)

    return decorated


# --- LIST ITEMS ---
@bp.route("/items", methods=["GET"])
def list_items():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 20)

    items = Item.query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=per_page
    )

    return jsonify(
        {
            "items": [i.to_dict() for i in items.items],
            "total": items.total,
            "page": items.page,
            "pages": items.pages,
        }
    )


# --- GET SINGLE ITEM ---
@bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())


# --- CREATE ITEM ---
@bp.route("/items", methods=["POST"])
@token_auth_required
def create_item():
    data = request.json or {}

    if "name" not in data:
        return jsonify({"error": "Field 'name' is required"}), 400

    item = Item(
        name=data.get("name"),
        description=data.get("description", ""),
        quantity=int(data.get("quantity", 0)),
        price=float(data.get("price", 0.0)),
        owner_id=request.user.id,
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


# --- GET TOKEN ---
@bp.route("/token", methods=["POST"])
def get_token():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = user.generate_api_token()

    return jsonify(
        {"token": token, "expires_in": current_app.config.get("JWT_EXP_DELTA_SECONDS")}
    )
