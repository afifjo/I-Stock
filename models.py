from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager
import pytz

# -----------------------------
# USER MODEL
# -----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    email = db.Column(db.String(120), unique=True)
    bio = db.Column(db.String(300))

    # avatar filename (default avatar included in static folder)
    avatar = db.Column(db.String(120), default="default.png")

    # Role-based access
    role = db.Column(db.String(20), default="user")  # 'admin' or 'user'
    is_approved = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=None)

    # Constructor helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# ITEM MODEL
# -----------------------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    # price removed

    # NEW: category and image filename
    category = db.Column(db.String(80), nullable=True)         # e.g. "electronics"
    image_filename = db.Column(db.String(200), nullable=True)  # store filename under static/uploads/
    
    # NEW: Assignment details
    assigned_to = db.Column(db.String(100), nullable=True)
    assigned_date = db.Column(db.Date, nullable=True)

    # NEW: Serial Number and Reference Code
    serial_number = db.Column(db.String(100), nullable=True)
    reference_code = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # optional: link item → user who added it
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='items')


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Link to the user who added this staff member (optional but good for multi-user apps)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='staff_members')
