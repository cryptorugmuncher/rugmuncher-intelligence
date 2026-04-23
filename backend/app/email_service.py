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

# ── Default Email Templates ────────────────────────────────────────────────
DEFAULT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "welcome": {
        "subject": "Welcome to RugMunch Intelligence, {{name}}!",
        "body_text": "Hi {{name}},\n\nWelcome to RugMunch Intelligence. Your account is active and you can start scanning contracts immediately.\n\nBest,\nThe RugMunch Team",
        "body_html": "<html><body><h2>Welcome to RugMunch Intelligence, {{name}}!</h2><p>Your account is active and you can start scanning contracts immediately.</p><p>Best,<br>The RugMunch Team</p></body></html>",
    },
    "notification": {
        "subject": "RugMunch Alert: {{title}}",
        "body_text": "Hi {{name}},\n\n{{message}}\n\nView details: {{link}}\n\nRugMunch Intelligence",
        "body_html": "<html><body><h2>{{title}}</h2><p>Hi {{name}},</p><p>{{message}}</p><p><a href='{{link}}'>View Details</a></p><p>RugMunch Intelligence</p></body></html>",
    },
    "scan_complete": {
        "subject": "Scan Complete: {{contract_address}}",
        "body_text": "Hi {{name}},\n\nYour scan for {{contract_address}} on {{chain}} is complete.\n\nRisk Score: {{risk_score}}/100\nVerdict: {{verdict}}\n\nView full report: {{report_link}}",
        "body_html": "<html><body><h2>Scan Complete</h2><p>Hi {{name}},</p><p>Your scan for <code>{{contract_address}}</code> on <strong>{{chain}}</strong> is complete.</p><p>Risk Score: <strong>{{risk_score}}/100</strong></p><p>Verdict: <strong>{{verdict}}</strong></p><p><a href='{{report_link}}'>View Full Report</a></p></body></html>",
    },
    "contact_form": {
        "subject": "Contact Form: {{subject}} from {{name}}",
        "body_text": "New contact submission:\n\nFrom: {{name}} <{{email}}>\nSubject: {{subject}}\n\nMessage:\n{{message}}\n\n— RugMunch Contact Form",
        "body_html": "<html><body><h2>New Contact Submission</h2><p><strong>From:</strong> {{name}} &lt;{{email}}&gt;</p><p><strong>Subject:</strong> {{subject}}</p><p><strong>Message:</strong></p><blockquote>{{message}}</blockquote><p>— RugMunch Contact Form</p></body></html>",
    },
    "newsletter": {
        "subject": "{{title}} — RugMunch Intelligence Update",
        "body_text": "Hi {{name}},\n\n{{content}}\n\nUnsubscribe: {{unsubscribe_link}}\nRugMunch Intelligence",
        "body_html": "<html><body><h2>{{title}}</h2><p>Hi {{name}},</p><div>{{content}}</div><p><a href='{{unsubscribe_link}}'>Unsubscribe</a></p><p>RugMunch Intelligence</p></body></html>",
    },
    "password_reset": {
        "subject": "Reset your RugMunch password",
        "body_text": "Hi {{name}},\n\nClick the link to reset your password:\n{{reset_link}}\n\nThis link expires in 1 hour.\n\nRugMunch Intelligence",
        "body_html": "<html><body><h2>Reset your RugMunch password</h2><p>Hi {{name}},</p><p><a href='{{reset_link}}'>Reset Password</a></p><p>This link expires in 1 hour.</p><p>RugMunch Intelligence</p></body></html>",
    },
    "partnership_inquiry": {
        "subject": "Partnership Inquiry from {{name}} — {{organization}}",
        "body_text": "New partnership inquiry:\n\nName: {{name}}\nOrganization: {{organization}}\nEmail: {{email}}\n\nMessage:\n{{message}}\n\n— RugMunch Partnerships",
        "body_html": "<html><body><h2>New Partnership Inquiry</h2><p><strong>Name:</strong> {{name}}</p><p><strong>Organization:</strong> {{organization}}</p><p><strong>Email:</strong> {{email}}</p><p><strong>Message:</strong></p><blockquote>{{message}}</blockquote><p>— RugMunch Partnerships</p></body></html>",
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
