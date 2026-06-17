import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_sales_email(to_email, subject, body_html):
    """
    Sends an HTML email using SMTP configuration from environment variables.
    """
    # Pull credentials securely from the environment
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD") 
    
    if not sender_email or not sender_password:
        print("[Error] Email credentials are not configured.")
        return False

    try:
        # Construct the email packet
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"SalesCatalyst AI <{sender_email}>"
        msg["To"] = to_email

        # Attach HTML body content
        msg.attach(MIMEText(body_html, "html"))

        # Open secure connection and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            
        print(f"[Success] Email sent seamlessly to {to_email}")
        return True
    
    except Exception as e:
        print(f"[Failure] Failed to dispatch email due to: {str(e)}")
        return False