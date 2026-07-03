# ============================================================
# email_service.py
# Sends emails to newly registered users with their credentials
# ============================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG


def send_credentials_email(recipient_email, recipient_name, username, password, role):
    sender_email = EMAIL_CONFIG["SENDER_EMAIL"]
    sender_password = EMAIL_CONFIG["SENDER_PASSWORD"]
    smtp_server = EMAIL_CONFIG["SMTP_SERVER"]
    smtp_port = EMAIL_CONFIG["SMTP_PORT"]
    sender_name = EMAIL_CONFIG["SENDER_NAME"]

    subject = "MakElize System - Your Account Has Been Created"

    body = f"""
Hello {recipient_name},

Your account has been created on the MakElize Emergency Maintenance System.

Your login details are below:

    Username : {username}
    Password : {password}
    Role     : {role}

Please log in at the system portal and change your password after your first login.

Do not share your password with anyone.

Regards,
{sender_name}
    """

    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return True, None
    except Exception as e:
        error_message = str(e)
        print("Email error:", error_message)
        return False, error_message