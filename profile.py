import os
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from werkzeug.security import generate_password_hash

# ----------------------------------------------------------
# BLUEPRINT
# ----------------------------------------------------------
profile = Blueprint("profile", __name__, template_folder="templates")

# ----------------------------------------------------------
# AVATAR UPLOAD FOLDER
# ----------------------------------------------------------
UPLOAD_FOLDER = "static/avatars"

# Create folder automatically if missing
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ==========================================================
# 1) VIEW PROFILE
# ==========================================================
@profile.route("/profile")
@login_required
def view_profile():
    return render_template("profile.html", user=current_user)


# ==========================================================
# 2) UPDATE AVATAR
# ==========================================================
@profile.route("/profile/avatar", methods=["POST"])
@login_required
def update_avatar():

    file = request.files.get("avatar")

    if not file:
        flash("Please upload a file.", "warning")
        return redirect(url_for("profile.view_profile"))

    filename = secure_filename(file.filename)

    if filename == "":
        flash("Invalid file.", "danger")
        return redirect(url_for("profile.view_profile"))

    # Save file
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    # Save to DB
    current_user.avatar = filename
    db.session.commit()

    flash("Avatar updated successfully!", "success")
    return redirect(url_for("profile.view_profile"))


# ==========================================================
# 3) EDIT PROFILE INFO (FINAL VERSION)
# ==========================================================
@profile.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        bio = request.form.get("bio")

        from models import User

        # -------- CHECK IF EMAIL ALREADY EXISTS --------
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != current_user.id:
            flash("❌ This email is already in use.", "danger")
            return redirect(url_for("profile.edit_profile"))

        # -------- CHECK IF USERNAME ALREADY EXISTS --------
        existing_username = User.query.filter_by(username=username).first()
        if existing_username and existing_username.id != current_user.id:
            flash("❌ Username already taken.", "danger")
            return redirect(url_for("profile.edit_profile"))

        # -------- SAVE CHANGES --------
        current_user.username = username
        current_user.email = email
        current_user.bio = bio

        db.session.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for("profile.view_profile"))

    return render_template("profile_edit.html", user=current_user)


# ==========================================================
# 4) CHANGE PASSWORD
# ==========================================================
@profile.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":
        current_pw = request.form.get("current_password")
        new_pw = request.form.get("new_password")
        confirm_pw = request.form.get("confirm_password")

        # Check current password
        if not current_user.check_password(current_pw):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("profile.change_password"))

        # Match new passwords
        if new_pw != confirm_pw:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("profile.change_password"))

        # Save new password
        current_user.password_hash = generate_password_hash(new_pw)
        db.session.commit()

        # Send new credentials email
        from email_utils import send_credentials_email
        send_credentials_email(current_user, new_pw)

        flash("Password changed successfully! New credentials sent to your email.", "success")
        return redirect(url_for("profile.view_profile"))

    return render_template("change_password.html", user=current_user)
