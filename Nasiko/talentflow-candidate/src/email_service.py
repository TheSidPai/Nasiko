"""
email_service.py
Real Gmail SMTP email delivery for TalentFlow HR.

Setup:
  1. Enable 2-Step Verification on your Google account.
  2. Go to myaccount.google.com → Security → App Passwords.
  3. Create an App Password for "Mail" / "Windows Computer".
  4. Add to .env:
       GMAIL_USER=your_gmail@gmail.com
       GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger("talentflow.email")

GMAIL_USER = "mc24bt016@iitdh.ac.in"
GMAIL_APP_PASSWORD = "ldnl zotc tjtt waqb"


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
) -> dict:
    """
    Send an email via Gmail SMTP using an App Password.

    Returns:
        {"success": True, "message": "..."} on success
        {"success": False, "error": "..."} on failure
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning("GMAIL_USER or GMAIL_APP_PASSWORD not configured.")
        return {
            "success": False,
            "error": (
                "Email credentials not configured. "
                "Add GMAIL_USER and GMAIL_APP_PASSWORD to your .env file."
            ),
        }

    if not to_email or "@" not in to_email:
        return {"success": False, "error": f"Invalid recipient email: '{to_email}'"}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"TalentFlow HR <{GMAIL_USER}>"
        msg["To"] = to_email

        # Attach plain text first, then HTML (email clients prefer HTML)
        if plain_body:
            msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return {"success": True, "message": f"Email sent successfully to {to_email}"}

    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail SMTP authentication failed. Check GMAIL_APP_PASSWORD.")
        return {
            "success": False,
            "error": (
                "Gmail authentication failed. "
                "Make sure you are using an App Password (not your account password). "
                "Go to myaccount.google.com → Security → App Passwords."
            ),
        }
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return {"success": False, "error": f"SMTP error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected email error: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to send email: {str(e)}"}


def build_offer_email(candidate_name: str, role: str, company: str = "TalentFlow Corp") -> tuple[str, str]:
    """Return (subject, html_body) for an offer email."""
    subject = f"Job Offer – {role} at {company}"
    html = f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a2e;">
  <div style="background:linear-gradient(135deg,#6c63ff,#4ecdc4);padding:32px;border-radius:12px 12px 0 0;">
    <h1 style="color:#fff;margin:0;font-size:1.6rem;">🎉 Congratulations, {candidate_name}!</h1>
  </div>
  <div style="background:#0f0f1a;padding:32px;border-radius:0 0 12px 12px;border:1px solid #2a2a4a;">
    <p style="color:#c9c9e0;line-height:1.7;">
      We are thrilled to extend an offer for the <strong style="color:#6c63ff;">{role}</strong> position at
      <strong>{company}</strong>. After a thorough review of your resume and background, we believe you are an
      outstanding fit for our team.
    </p>
    <p style="color:#c9c9e0;line-height:1.7;">
      Our HR team will reach out within <strong>2 business days</strong> with the full offer letter,
      compensation details, and next steps.
    </p>
    <div style="background:#1a1a2e;border-left:4px solid #6c63ff;padding:16px;border-radius:0 8px 8px 0;margin:24px 0;">
      <p style="color:#4ecdc4;margin:0;font-weight:bold;">What happens next?</p>
      <ul style="color:#c9c9e0;margin:8px 0 0 0;padding-left:20px;">
        <li>Formal offer letter via email within 2 business days</li>
        <li>Background verification process</li>
        <li>Onboarding schedule confirmation</li>
      </ul>
    </div>
    <p style="color:#c9c9e0;line-height:1.7;">
      Please feel free to reach out if you have any questions. We look forward to welcoming you aboard!
    </p>
    <p style="color:#6c63ff;font-weight:bold;margin-top:32px;">Warm regards,<br>TalentFlow HR Team</p>
  </div>
</div>
"""
    return subject, html


def build_rejection_email(candidate_name: str, role: str, company: str = "TalentFlow Corp") -> tuple[str, str]:
    """Return (subject, html_body) for a rejection email."""
    subject = f"Application Update – {role} at {company}"
    html = f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a2e;">
  <div style="background:linear-gradient(135deg,#2a2a4a,#3a3a5c);padding:32px;border-radius:12px 12px 0 0;">
    <h1 style="color:#c9c9e0;margin:0;font-size:1.6rem;">Application Update</h1>
    <p style="color:#8888aa;margin:8px 0 0 0;">Regarding your application for {role}</p>
  </div>
  <div style="background:#0f0f1a;padding:32px;border-radius:0 0 12px 12px;border:1px solid #2a2a4a;">
    <p style="color:#c9c9e0;line-height:1.7;">Dear {candidate_name},</p>
    <p style="color:#c9c9e0;line-height:1.7;">
      Thank you for your interest in the <strong style="color:#6c63ff;">{role}</strong> position at {company}
      and for the time you invested in the application process.
    </p>
    <p style="color:#c9c9e0;line-height:1.7;">
      After careful consideration, we have decided to move forward with another candidate whose experience
      more closely matches our current needs. This decision was not easy, as we received many strong applications.
    </p>
    <div style="background:#1a1a2e;border-left:4px solid #4ecdc4;padding:16px;border-radius:0 8px 8px 0;margin:24px 0;">
      <p style="color:#4ecdc4;margin:0;">We genuinely appreciate your enthusiasm for {company} and encourage you
      to apply for future openings that align with your skills.</p>
    </div>
    <p style="color:#c9c9e0;line-height:1.7;">
      We wish you all the best in your career journey.
    </p>
    <p style="color:#6c63ff;font-weight:bold;margin-top:32px;">Best regards,<br>TalentFlow HR Team</p>
  </div>
</div>
"""
    return subject, html
