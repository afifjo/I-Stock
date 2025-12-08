from flask_mail import Message
from flask import current_app, render_template, url_for
from extensions import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_email(subject, recipients, text_body, html_body=None):
    # Check if email is configured
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        print(f"Email not configured. Would have sent to {recipients}: {subject}")
        return
    
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Send asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_credentials_email(user, password):
    subject = "Your Account Credentials - IWATCH-INV"
    text_body = f"""
    Welcome to IWATCH-INV!
    
    Your account has been created.
    
    Username: {user.username}
    Password: {password}
    
    Please change your password after logging in.
    """
    send_email(subject, [user.email], text_body)

def send_password_reset_email(user, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Reset Your Password - IWATCH-INV"
    text_body = f"""
    To reset your password, visit the following link:
    {reset_url}
    
    If you did not make this request then simply ignore this email and no changes will be made.
    """
    send_email(subject, [user.email], text_body)
