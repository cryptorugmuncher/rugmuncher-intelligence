#!/usr/bin/env python3
"""
Email Management Router
=======================
Handles contact forms, email templates, logs, and forwarding rules.
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.email_service import (
    send_email,
    send_templated_email,
    get_business_emails,
    get_email_status,
    DEFAULT_TEMPLATES,
)

router = APIRouter(prefix="/api/v1", tags=["email"])

_supabase = None

def _get_supabase():
    global _supabase
    if _supabase is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
            if url and key:
                _supabase = create_client(url, key)
        except Exception as e:
            print(f"[EMAIL] Supabase init failed: {e}")
    return _supabase


def _now() -> str:
    return datetime.utcnow().isoformat()


def _require_admin(request: Request):
    # Simple admin check via header or token claim
    # In production, integrate with your auth middleware
    token = request.headers.get("Authorization", "")
    # Allow through for now if any token present; tighten later
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


# ── PYDANTIC MODELS ──
class ContactFormRequest(BaseModel):
    name: str = Field(..., max_length=200)
    email: str = Field(..., max_length=200)
    subject: str = Field(..., max_length=300)
    message: str = Field(..., max_length=5000)


class SendEmailRequest(BaseModel):
    to: str = Field(..., max_length=200)
    template_name: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    from_alias: Optional[str] = "admin"


class TemplateUpdateRequest(BaseModel):
    subject: str
    html_body: Optional[str] = None
    text_body: Optional[str] = None


class ReplyContactRequest(BaseModel):
    reply_message: str = Field(..., max_length=5000)


class ForwardingRuleRequest(BaseModel):
    alias_address: str = Field(..., max_length=200)
    forward_to: str = Field(..., max_length=200)
    description: Optional[str] = None
    active: bool = True


# ── PUBLIC ENDPOINTS ──

@router.post("/contact")
async def submit_contact(form: ContactFormRequest):
    """Public contact form submission."""
    sb = _get_supabase()
    if sb:
        sb.table("contact_submissions").insert({
            "name": form.name,
            "email": form.email,
            "subject": form.subject,
            "message": form.message,
            "status": "new",
            "created_at": _now(),
        }).execute()

    # Notify admin
    biz = get_business_emails().get("support", {})
    try:
        send_templated_email(
            to=biz.get("forward_to", os.getenv("EMAIL_USER", "")),
            template_name="contact_form",
            context={
                "name": form.name,
                "email": form.email,
                "subject": form.subject,
                "message": form.message,
            },
            from_email=biz.get("address"),
            from_name=biz.get("display"),
            reply_to=form.email,
        )
    except Exception as e:
        print(f"[EMAIL] Contact notification failed: {e}")

    return {"success": True, "message": "Contact submission received"}


@router.get("/email/business-emails")
async def list_business_emails():
    """List managed business email accounts."""
    return {"accounts": get_business_emails()}


# ── ADMIN ENDPOINTS ──

@router.post("/admin/email/send")
async def admin_send_email(req: SendEmailRequest, request: Request):
    """Send an email (admin only)."""
    _require_admin(request)

    biz = get_business_emails().get(req.from_alias or "admin", {})
    from_email = biz.get("address")
    from_name = biz.get("display")

    if req.template_name:
        result = send_templated_email(
            to=req.to,
            template_name=req.template_name,
            context={"name": req.to, "message": req.body_text or ""},
            from_email=from_email,
            from_name=from_name,
        )
    else:
        result = send_email(
            to=req.to,
            subject=req.subject or "No Subject",
            body_text=req.body_text or "",
            body_html=req.body_html,
            from_email=from_email,
            from_name=from_name,
        )

    # Log to DB
    sb = _get_supabase()
    if sb:
        sb.table("email_logs").insert({
            "to_address": req.to,
            "from_address": from_email,
            "template_name": req.template_name,
            "subject": req.subject or req.template_name,
            "status": "sent" if result.get("success") else "failed",
            "error_msg": result.get("error"),
            "sent_at": _now(),
        }).execute()

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Send failed"))
    return result


@router.get("/admin/email/logs")
async def list_email_logs(request: Request, limit: int = 50, offset: int = 0):
    """Paginated email logs (admin only)."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        return {"items": [], "total": 0}
    result = sb.table("email_logs").select("*", count="exact").order("sent_at", desc=True).range(offset, offset + limit - 1).execute()
    return {
        "items": result.data or [],
        "total": result.count if hasattr(result, "count") and result.count is not None else len(result.data or []),
        "limit": limit,
        "offset": offset,
    }


@router.get("/admin/email/templates")
async def list_templates(request: Request):
    """List email templates."""
    _require_admin(request)
    sb = _get_supabase()
    db_templates = []
    if sb:
        res = sb.table("email_templates").select("*").execute()
        db_templates = res.data or []

    # Merge with defaults
    merged = []
    for name, tpl in DEFAULT_TEMPLATES.items():
        db = next((x for x in db_templates if x["name"] == name), None)
        merged.append({
            "name": name,
            "subject": db["subject"] if db else tpl["subject"],
            "html_body": db["html_body"] if db else tpl.get("body_html"),
            "text_body": db["text_body"] if db else tpl.get("body_text"),
            "is_default": db is None,
        })
    return {"templates": merged}


@router.put("/admin/email/templates/{name}")
async def update_template(name: str, req: TemplateUpdateRequest, request: Request):
    """Update or override a template."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    upsert = {
        "name": name,
        "subject": req.subject,
        "html_body": req.html_body,
        "text_body": req.text_body,
        "updated_at": _now(),
    }
    sb.table("email_templates").upsert(upsert, on_conflict="name").execute()
    return {"success": True, "name": name}


@router.get("/admin/email/contact-submissions")
async def list_contact_submissions(request: Request, status: Optional[str] = None, limit: int = 50, offset: int = 0):
    """List contact form submissions."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        return {"items": [], "total": 0}
    q = sb.table("contact_submissions").select("*", count="exact").order("created_at", desc=True).range(offset, offset + limit - 1)
    if status:
        q = q.eq("status", status)
    result = q.execute()
    return {
        "items": result.data or [],
        "total": result.count if hasattr(result, "count") and result.count is not None else len(result.data or []),
        "limit": limit,
        "offset": offset,
    }


@router.post("/admin/email/contact-submissions/{submission_id}/reply")
async def reply_contact(submission_id: str, req: ReplyContactRequest, request: Request):
    """Reply to a contact submission via email."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")

    sub = sb.table("contact_submissions").select("*").eq("id", submission_id).execute()
    if not sub.data:
        raise HTTPException(status_code=404, detail="Submission not found")

    item = sub.data[0]
    result = send_email(
        to=item["email"],
        subject=f"Re: {item['subject']}",
        body_text=req.reply_message,
        from_email=get_business_emails().get("support", {}).get("address"),
        from_name="RugMunch Support",
    )

    sb.table("contact_submissions").update({
        "status": "replied",
        "reply_message": req.reply_message,
        "replied_at": _now(),
    }).eq("id", submission_id).execute()

    return {"success": result.get("success"), "error": result.get("error")}


@router.get("/admin/email/forwarding-rules")
async def list_forwarding_rules(request: Request):
    """List email forwarding rules."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        return {"rules": list(get_business_emails().values())}
    result = sb.table("email_forwarding_rules").select("*").order("created_at", desc=True).execute()
    return {"rules": result.data or []}


@router.post("/admin/email/forwarding-rules")
async def create_forwarding_rule(req: ForwardingRuleRequest, request: Request):
    """Create a forwarding rule."""
    _require_admin(request)
    sb = _get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database unavailable")
    result = sb.table("email_forwarding_rules").insert({
        "alias_address": req.alias_address,
        "forward_to": req.forward_to,
        "description": req.description,
        "active": req.active,
        "created_at": _now(),
    }).execute()
    return {"success": True, "rule": result.data[0] if result.data else None}
