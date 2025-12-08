from flask import Blueprint, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Item

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/")
@login_required
def home():

    # Show only items that belong to logged-in user
    total_items = Item.query.filter_by(user_id=current_user.id).count()

    low_stock = Item.query.filter(
        Item.user_id == current_user.id,
        Item.quantity < 5
    ).all()

    latest_items = Item.query.filter_by(
        user_id=current_user.id
    ).order_by(Item.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_items=total_items,
        low_stock=low_stock,
        latest_items=latest_items
    )
