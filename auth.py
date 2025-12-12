from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime
from email_utils import send_credentials_email, send_password_reset_email
from itsdangerous import URLSafeTimedSerializer

bp = Blueprint("auth", __name__, template_folder="templates")


# ===========================
# LOGIN
# ===========================
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_approved:
            flash("Your account is pending approval. Please contact an admin.", "warning")
            return redirect(url_for("auth.login"))

        # Update last login AFTER successful login
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user)

        flash("Logged in successfully!", "success")

        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("login.html", form=form)


# ===========================
# REGISTER
# ===========================
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Check if username exists
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash("Username already taken.", "warning")
            return redirect(url_for("auth.register"))

        # Check email duplicate
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash("Email already in use.", "danger")
            return redirect(url_for("auth.register"))

        # Create user
        role = form.role.data
        admin_code = form.admin_code.data
        is_approved = False

        if role == "admin":
            if admin_code == "afif":
                is_approved = True  # Auto-approve if code is correct
            else:
                flash("Invalid Admin Code. Registration rejected.", "danger")
                return redirect(url_for("auth.register"))
        else:
            # Regular users need approval
            is_approved = False

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=role,
            is_approved=is_approved,
            created_at=datetime.utcnow()
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        # Send credentials email
        try:
            send_credentials_email(new_user, form.password.data)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")
            flash("Account created, but failed to send email credentials.", "warning")

        if is_approved:
            flash("Account created! Credentials sent to your email.", "success")
        else:
            flash("Account created! Please wait for admin approval. Credentials sent to your email.", "info")
            
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


# ===========================
# LOGOUT
# ===========================
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.login"))


# ===========================
# PASSWORD RESET
# ===========================
@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = ts.dumps(user.email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
            send_password_reset_email(user, token)
        
        flash("If an account with that email exists, a password reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
        
    return render_template("forgot_password.html", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=3600)
    except:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))
        
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        
        # Send new credentials email (optional, but requested "same for changing password")
        # Actually user knows the password they just set, but let's send it as confirmation/record if desired.
        # The request said "same for changing password", which implies sending the new password.
        try:
            send_credentials_email(user, form.password.data)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")
            flash("Password updated, but failed to send email confirmation.", "warning")
        
        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for("auth.login"))
        
    return render_template("reset_password.html", form=form)
