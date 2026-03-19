from flask_mail import Message
from flask import url_for
from src.extensions import mail

def send_reset_email(to_email, token):
    reset_link = url_for(
        "auth.reset_password",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Password Reset Request",
        recipients=[to_email]
    )

    msg.body = f"""
Click the link below to reset your password.
This link expires in 3 minutes.


{reset_link}
"""
    
    # HTML version (clickable link, styled)
    msg.html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2>Password Reset Request</h2>
    <p>We received a request to reset your password. Click the button below to reset it:</p>
    <p style="text-align: center;">
      <a href="{reset_link}" style="
          background-color: #007bff;
          color: white;
          padding: 10px 20px;
          text-decoration: none;
          border-radius: 5px;
          display: inline-block;
      ">Reset Password</a>
    </p>
    <p>This link will expire in <strong>3 minutes</strong>.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <hr>
    <p style="font-size: 0.9em; color: #555;">&copy; 2025 Your Company. All rights reserved.</p>
  </body>
</html>
"""

    mail.send(msg)
