"""
Email Service — Transactional & Marketing Email Management
Supports SMTP (Gmail) and can be extended to Resend/SendGrid/AWS SES.
"""
import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from jinja2 import Template

# ── Configuration ───────────────────────────────────────────────────────────
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("ADMIN_EMAIL", "admin@cryptorugmunch.com")
EMAIL_ENABLED = bool(EMAIL_HOST and EMAIL_USER and EMAIL_PASSWORD)

# Business email addresses managed by the platform
BUSINESS_EMAILS: Dict[str, Dict[str, str]] = {
    "admin": {
        "address": "admin@cryptorugmunch.com",
        "display": "RugMunch Admin",
        "purpose": "Platform administration, user escalations",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "biz": {
        "address": "biz@rugmunch.io",
        "display": "RugMunch Business",
        "purpose": "Business inquiries, partnerships, B2B",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "work": {
        "address": "work@cryptorugmunch.com",
        "display": "RugMunch Work",
        "purpose": "Internal team communications, HR",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "support": {
        "address": "support@cryptorugmunch.com",
        "display": "RugMunch Support",
        "purpose": "User support tickets, help requests",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "hello": {
        "address": "hello@rugmunch.io",
        "display": "RugMunch Hello",
        "purpose": "General inquiries, press, community",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "legal": {
        "address": "legal@cryptorugmunch.com",
        "display": "RugMunch Legal",
        "purpose": "DMCA, compliance, legal notices",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "partnerships": {
        "address": "partnerships@rugmunch.io",
        "display": "RugMunch Partnerships",
        "purpose": "Exchange listings, API partnerships, integrations",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "press": {
        "address": "press@cryptorugmunch.com",
        "display": "RugMunch Press",
        "purpose": "Media inquiries, press releases, interviews",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "security": {
        "address": "security@cryptorugmunch.com",
        "display": "RugMunch Security",
        "purpose": "Bug bounty, vulnerability reports, incident response",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
    "notifications": {
        "address": "notifications@rugmunch.io",
        "display": "RugMunch Notifications",
        "purpose": "Automated platform notifications, alerts",
        "forward_to": EMAIL_USER or "cryptorugmuncher@gmail.com",
    },
}


def send_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an email via SMTP. Returns status dict."""
    if not EMAIL_ENABLED:
        return {"success": False, "error": "Email not configured"}

    sender = from_email or EMAIL_FROM
    sender_name = from_name or "RugMunch Intelligence"
    from_header = f"{sender_name} <{sender}>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_header
    msg["To"] = to
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(sender, [to], msg.as_string())
        return {"success": True, "to": to, "subject": subject, "sent_at": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"success": False, "error": str(e), "to": to, "subject": subject}


def render_template(template_name: str, context: Dict[str, Any]) -> Dict[str, str]:
    """Render a Jinja2 email template. Returns {subject, body_text, body_html}."""
    tpl = DEFAULT_TEMPLATES.get(template_name)
    if not tpl:
        raise ValueError(f"Unknown template: {template_name}")
    return {
        "subject": Template(tpl["subject"]).render(**context),
        "body_text": Template(tpl["body_text"]).render(**context),
        "body_html": Template(tpl.get("body_html", "")).render(**context) if tpl.get("body_html") else None,
    }


def send_templated_email(to: str, template_name: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Send an email using a named template."""
    rendered = render_template(template_name, context)
    return send_email(
        to=to,
        subject=rendered["subject"],
        body_text=rendered["body_text"],
        body_html=rendered.get("body_html"),
        **kwargs,
    )


def get_business_emails() -> Dict[str, Dict[str, str]]:
    """Return all managed business email accounts."""
    return BUSINESS_EMAILS


def get_email_status() -> Dict[str, Any]:
    """Return email service health/status."""
    return {
        "enabled": EMAIL_ENABLED,
        "host": EMAIL_HOST,
        "port": EMAIL_PORT,
        "user": EMAIL_USER,
        "from": EMAIL_FROM,
        "accounts_configured": len(BUSINESS_EMAILS),
    }
