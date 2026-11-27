import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional


def send_verification_email(to_email: str, code: str, user_name: Optional[str] = None) -> bool:
    """
    Send 6-digit OTP verification email via SMTP (e.g. Gmail SMTP or Brevo/SendGrid).
    If SMTP_USER or SMTP_PASSWORD is not set in backend/.env, gracefully logs the OTP
    to the console/logs without breaking the signup flow.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    sender_name = os.getenv("SMTP_SENDER_NAME", "ParkKaro")

    # If no SMTP credentials provided, log OTP code for dev/test
    if not smtp_user or not smtp_password:
        print(f"📧 [Email Service - Mock Mode] Verification code for {to_email}: {code}")
        return False

    name_str = (user_name or "Driver").strip()
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{code} is your ParkKaro Verification Code"
        msg["From"] = f"{sender_name} <{smtp_user}>"
        msg["To"] = to_email

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
            .card {{ max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .logo {{ display: inline-block; background: #FFCA20; color: #111827; padding: 6px 14px; border-radius: 999px; font-weight: 900; font-size: 16px; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: 800; color: #1e293b; margin: 0 0 10px 0; }}
            .text {{ font-size: 14px; color: #475569; line-height: 1.6; }}
            .otp-box {{ background: #FEF08A; border: 2px dashed #EAB308; border-radius: 12px; padding: 18px; text-align: center; margin: 24px 0; }}
            .otp-code {{ font-size: 32px; font-weight: 900; letter-spacing: 8px; color: #111827; font-family: monospace; }}
            .footer {{ font-size: 12px; color: #94a3b8; margin-top: 24px; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 16px; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo">parkkaro</div>
            <h2 class="title">Driver Account Verification</h2>
            <p class="text">Hello <strong>{name_str}</strong>,</p>
            <p class="text">Thank you for registering on ParkKaro. Please use the following 6-digit verification code to activate your verified driver account in Supabase:</p>
            <div class="otp-box">
              <div class="otp-code">{code}</div>
            </div>
            <p class="text">Enter this code on the verification screen to unlock live parking spot booking.</p>
            <div class="footer">
              If you did not request this code, you can safely ignore this email.<br/>
              &copy; 2026 ParkKaro Smart Parking Intelligence
            </div>
          </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"📧 [Email Service] OTP successfully sent to {to_email}")
        return True
    except Exception as exc:
        print(f"⚠️ [Email Service Warning] Failed to send email to {to_email}: {exc}")
        return False
