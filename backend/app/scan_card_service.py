"""
🖼️ Scan Card Image Service
==========================
Generates shareable PNG scan cards for social sharing.
Used by both the backend API and Telegram bot.
"""

import os
import io
import base64
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Try to load a font; fallback to default if not available
def _get_font(size: int):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_scan_card(
    token: str,
    chain: str = "SOL",
    scan_type: str = "SECURITY SCAN",
    risk_score: Optional[int] = None,
    risk_level: Optional[str] = None,
    verdict: Optional[str] = None,
    red_flags: Optional[List[str]] = None,
    ai_consensus: Optional[str] = None,
    width: int = 800,
    height: int = 1000,
) -> bytes:
    """Generate a scan card PNG image. Returns raw PNG bytes."""

    # Background
    img = Image.new("RGB", (width, height), "#0a0a0f")
    draw = ImageDraw.Draw(img)

    # Risk colors
    if risk_score is None:
        gradient_top, gradient_bottom, accent = "#4b5563", "#1f2937", "#9ca3af"
    elif risk_score >= 70:
        gradient_top, gradient_bottom, accent = "#dc2626", "#7f1d1d", "#f87171"
    elif risk_score >= 40:
        gradient_top, gradient_bottom, accent = "#f97316", "#dc2626", "#fb923c"
    elif risk_score >= 20:
        gradient_top, gradient_bottom, accent = "#eab308", "#f97316", "#facc15"
    else:
        gradient_top, gradient_bottom, accent = "#10b981", "#059669", "#34d399"

    # Draw gradient header
    for y in range(300):
        ratio = y / 300
        r = int(int(gradient_top[1:3], 16) * (1 - ratio) + int(gradient_bottom[1:3], 16) * ratio)
        g = int(int(gradient_top[3:5], 16) * (1 - ratio) + int(gradient_bottom[3:5], 16) * ratio)
        b = int(int(gradient_top[5:7], 16) * (1 - ratio) + int(gradient_bottom[5:7], 16) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Top accent bar
    draw.rectangle([(0, 0), (width, 6)], fill=accent)

    # Fonts
    font_title = _get_font(32)
    font_score = _get_font(96)
    font_label = _get_font(20)
    font_body = _get_font(18)
    font_small = _get_font(14)
    font_tiny = _get_font(12)

    # Logo area
    logo_x, logo_y = 40, 40
    draw.rounded_rectangle(
        [(logo_x, logo_y), (logo_x + 50, logo_y + 50)],
        radius=10,
        fill="#8b5cf6",
    )
    draw.text((logo_x + 60, logo_y + 8), "Rug Munch", font=font_title, fill="white")
    draw.text((logo_x + 60, logo_y + 42), scan_type, font=font_small, fill="#9ca3af")

    # Risk score circle
    cx, cy = width // 2, 320
    radius = 120
    for r in range(radius, radius - 8, -1):
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=accent, width=1)
    draw.ellipse([(cx - radius + 8, cy - radius + 8), (cx + radius - 8, cy + radius - 8)], fill="#0a0a0f")

    score_text = str(risk_score) if risk_score is not None else "?"
    bbox = draw.textbbox((0, 0), score_text, font=font_score)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - 50), score_text, font=font_score, fill=accent)

    out_of = "/100"
    bbox2 = draw.textbbox((0, 0), out_of, font=font_label)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx - tw2 // 2, cy + 30), out_of, font=font_label, fill="#6b7280")

    # Risk label
    label = risk_level or ("CRITICAL" if risk_score and risk_score >= 70 else
                            "HIGH RISK" if risk_score and risk_score >= 40 else
                            "MEDIUM RISK" if risk_score and risk_score >= 20 else
                            "SAFE" if risk_score is not None else "UNKNOWN")
    bbox3 = draw.textbbox((0, 0), label, font=font_label)
    tw3 = bbox3[2] - bbox3[0]
    draw.text((cx - tw3 // 2, cy + radius + 20), label, font=font_label, fill=accent)

    # Verdict
    y_pos = cy + radius + 70
    if verdict:
        words = verdict.split()
        lines = []
        line = []
        for word in words:
            test_line = " ".join(line + [word])
            bbox_test = draw.textbbox((0, 0), test_line, font=font_small)
            if bbox_test[2] - bbox_test[0] < width - 80:
                line.append(word)
            else:
                lines.append(" ".join(line))
                line = [word]
        if line:
            lines.append(" ".join(line))
        for line_text in lines[:3]:
            bbox_line = draw.textbbox((0, 0), line_text, font=font_small)
            tw_line = bbox_line[2] - bbox_line[0]
            draw.text((cx - tw_line // 2, y_pos), line_text, font=font_small, fill="#9ca3af")
            y_pos += 24

    # Token box
    y_pos += 20
    box_margin = 40
    draw.rounded_rectangle(
        [(box_margin, y_pos), (width - box_margin, y_pos + 90)],
        radius=12,
        fill="#111118",
        outline="#22222e",
        width=1,
    )
    draw.text((box_margin + 16, y_pos + 12), "TOKEN / ADDRESS", font=font_tiny, fill="#6b7280")

    token_display = token if len(token) < 42 else f"{token[:8]}...{token[-6:]}"
    draw.text((box_margin + 16, y_pos + 36), token_display, font=font_body, fill="white")

    chain_text = f"{chain}"
    if ai_consensus:
        chain_text += f"  •  AI: {ai_consensus}"
    draw.text((box_margin + 16, y_pos + 62), chain_text, font=font_tiny, fill="#a78bfa")

    # Red flags
    y_pos += 110
    if red_flags:
        for i, flag in enumerate(red_flags[:3]):
            flag_text = f"⚠ {flag[:50]}"
            draw.text((box_margin, y_pos), flag_text, font=font_small, fill="#f87171")
            y_pos += 26
        if len(red_flags) > 3:
            draw.text((box_margin, y_pos), f"+{len(red_flags) - 3} more", font=font_tiny, fill="#6b7280")
            y_pos += 20

    # Footer
    y_pos = height - 50
    draw.text((box_margin, y_pos), "rugmunch.io", font=font_tiny, fill="#374151")
    draw.text((width - 200, y_pos), "Don't Get Rugged", font=font_tiny, fill="#374151")

    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def generate_scan_card_base64(**kwargs) -> str:
    """Generate a scan card and return as base64 data URI."""
    png_bytes = generate_scan_card(**kwargs)
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"
