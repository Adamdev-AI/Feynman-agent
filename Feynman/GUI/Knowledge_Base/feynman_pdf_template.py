import os
import json
from functools import partial
from xml.sax.saxutils import escape as _xml_escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
import webbrowser

def _register(logical_name, candidates, fallback):
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont(logical_name, path))
                return logical_name
            except Exception:
                continue
    return fallback

FONT_BODY = _register("Body", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
    r"C:\Windows\Fonts\arial.ttf",
], "Helvetica")

FONT_BODY_BOLD = _register("Body-Bold", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
], "Helvetica-Bold")

FONT_BODY_ITALIC = _register("Body-Italic", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    r"C:\Windows\Fonts\segoeuii.ttf",
    r"C:\Windows\Fonts\calibrii.ttf",
    r"C:\Windows\Fonts\ariali.ttf",
], "Helvetica-Oblique")

FONT_DISPLAY_BOLD = _register("Display-Bold", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
], "Helvetica-Bold")

PALETTE = {
    "page_bg":     colors.HexColor("#0b0e15"),
    "card_bg":     colors.HexColor("#161b22"),
    "card_border": colors.HexColor("#2a3140"),
    "hairline":    colors.HexColor("#424754"),
    "ink":         colors.HexColor("#d9e3f6"),
    "muted":       colors.HexColor("#8c909f"),
    "muted_2":     colors.HexColor("#c2c6d6"),
    "accent":      colors.HexColor("#34d399"),
    "accent_bg":   colors.HexColor("#0f2a22"),
    "accent_bd":   colors.HexColor("#245c49"),
    "success":     colors.HexColor("#4edea3"),
    "success_bg":  colors.HexColor("#123328"),
    "success_bd":  colors.HexColor("#2f6b53"),
    "warning":     colors.HexColor("#ffb95f"),
    "warning_bg":  colors.HexColor("#2e2312"),
    "warning_bd":  colors.HexColor("#6b502a"),
    "danger":      colors.HexColor("#ffb4ab"),
    "danger_bg":   colors.HexColor("#2a1216"),
    "danger_bd":   colors.HexColor("#5c2b2f"),
    "category_bg": colors.HexColor("#2b3544"),
    "chip_bg":     colors.HexColor("#212b39"),
    "probe_bg":    colors.HexColor("#121c2a"),
    "quote_bg":    colors.HexColor("#101722"),
    "ring_bg":     colors.HexColor("#2b2f3a"),
    "ring_good":   colors.HexColor("#2ecc71"),
    "ring_mid":    colors.HexColor("#f1c40f"),
    "ring_low":    colors.HexColor("#e74c3c"),
    "white":       colors.white,
}

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
FRAME_W = PAGE_W - 2 * MARGIN
INNER_W = FRAME_W - 30  # usable width inside a 15pt-padded card

base_styles = getSampleStyleSheet()
styles = {}

def _style(name, **kw):
    styles[name] = ParagraphStyle(name, parent=base_styles["Normal"], **kw)

_style("H1", fontName=FONT_DISPLAY_BOLD, fontSize=19, leading=23,
       textColor=PALETTE["accent"], spaceBefore=14, spaceAfter=10)
_style("H2", fontName=FONT_BODY_BOLD, fontSize=12.5, leading=16,
       textColor=PALETTE["ink"], spaceBefore=2, spaceAfter=6)
_style("CardTitle", fontName=FONT_BODY_BOLD, fontSize=13.5, leading=17,
       textColor=PALETTE["ink"])
_style("Body", fontName=FONT_BODY, fontSize=9.5, leading=14.5,
       textColor=PALETTE["ink"])
_style("BodyMuted", fontName=FONT_BODY, fontSize=9.5, leading=14.5,
       textColor=PALETTE["muted_2"])
_style("Overview", fontName=FONT_BODY, fontSize=10.5, leading=16.5,
       textColor=PALETTE["muted_2"])
_style("SectionLabel", fontName=FONT_BODY_BOLD, fontSize=8.6, leading=12,
       textColor=PALETTE["muted_2"])
_style("PanelLabel", fontName=FONT_BODY_BOLD, fontSize=9, leading=12,
       textColor=PALETTE["ink"])
_style("Bullet", fontName=FONT_BODY, fontSize=9.3, leading=14,
       textColor=PALETTE["muted_2"], leftIndent=14, bulletIndent=0)
_style("Quote", fontName=FONT_BODY_ITALIC, fontSize=9, leading=13.5,
       textColor=PALETTE["muted_2"])
_style("StatLabel", fontName=FONT_BODY, fontSize=8.3, leading=11,
       textColor=PALETTE["muted"], alignment=TA_CENTER)
_style("StepText", fontName=FONT_BODY, fontSize=9.5, leading=14.5,
       textColor=PALETTE["ink"])
_style("CoverSub", fontName=FONT_BODY, fontSize=13, leading=18,
       textColor=colors.HexColor("#b9c4de"))

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def _pick_quote(chat_history, max_len=220):
    history = _as_list(chat_history)
    assistant_msgs = [m.get("content", "") for m in history
                       if isinstance(m, dict) and m.get("role") == "assistant" and m.get("content")]
    if not assistant_msgs:
        return None
    best = max(assistant_msgs, key=len)
    best = best.replace("\n", " ").strip()
    if len(best) > max_len:
        best = best[:max_len].rsplit(" ", 1)[0] + "..."
    return best


def _clean_text(value):
    if not isinstance(value, str):
        return ""
    return value.strip()


def _safe_text(value):
    """
    Clean + XML-escape a string that will be embedded in a reportlab
    Paragraph. Paragraph text is parsed as a tiny markup language, so a
    raw '<' or '&' from a chat transcript or LLM-authored note (think:
    "List<T>", "3 < 5", "if a < b") can be read as the start of a broken
    tag and raise a ValueError deep inside doc.build(), taking the whole
    report down with it. Escaping first makes those characters literal
    text again.

    Only call this on strings destined for Paragraph(). Text drawn
    directly on the canvas (c.drawString / c.drawCentredString, as used
    for chips, pills, and quotes) is NOT XML-parsed and must stay raw --
    escaping it there would print a literal "&amp;" instead of "&".
    """
    text = value if isinstance(value, str) else ("" if value is None else str(value))
    return _xml_escape(text.strip())


def _safe_int(value, default=0):
    """
    Coerce DB-ish numeric input to int without blowing up on strings
    like '75.5' (int('75.5') raises ValueError, only int(float('75.5'))
    works) or on None/empty values.
    """
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            return default


def _normalize_deep_dive(raw):
    raw = raw or {}
    return {
        "whats_working": _safe_text(raw.get("whats_working")),
        "root_cause": _safe_text(raw.get("root_cause")),
        "fix": _safe_text(raw.get("fix")),
    }


def _normalize_card(card):
    return {
        "id": card.get("id", ""),
        "name": _safe_text(card.get("card_name") or "Untitled card"),
        "status": (card.get("verified_or_wrong") or "unverified").lower(),
        "category": card.get("header_category_name") or "Uncategorized",
        "progress": _safe_int(card.get("progress_number")),
        "concepts": _as_list(card.get("key_concepts")),
        "probes": _as_list(card.get("last_probes")) or [],
        "gap": _safe_text(card.get("gap")),
        "quote": _pick_quote(card.get("chat_history")),
        "deep_dive": _normalize_deep_dive(card.get("deep_dive")),
    }


def _normalize_narrative(narrative):
    narrative = narrative or {}
    return {
        "overview": _safe_text(narrative.get("overview")),
        "strengths": [_safe_text(s) for s in (narrative.get("strengths") or []) if _clean_text(s)],
        "growth_areas": [_safe_text(s) for s in (narrative.get("growth_areas") or []) if _clean_text(s)],
        "study_plan": [_safe_text(s) for s in (narrative.get("study_plan") or []) if _clean_text(s)],
    }

def _icon_check(c, cx, cy, r, color):
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(cx - r, cy)
    p.lineTo(cx - r * 0.2, cy - r * 0.8)
    p.lineTo(cx + r, cy + r * 0.75)
    c.drawPath(p, stroke=1, fill=0)


def _icon_alert(c, cx, cy, r, color):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.4)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setLineWidth(1.6)
    c.line(cx, cy + r * 0.45, cx, cy - r * 0.05)
    c.circle(cx, cy - r * 0.45, 0.9, stroke=0, fill=1)


def _icon_arrow(c, cx, cy, r, color):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.6)
    c.setLineCap(1)
    c.line(cx - r, cy, cx + r * 0.4, cy)
    p = c.beginPath()
    p.moveTo(cx + r * 0.4, cy + r * 0.55)
    p.lineTo(cx + r, cy)
    p.lineTo(cx + r * 0.4, cy - r * 0.55)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


ICONS = {"check": _icon_check, "alert": _icon_alert, "arrow": _icon_arrow}


class Pill(Flowable):
    def __init__(self, text, bg, fg, border, size=7.6):
        super().__init__()
        self.text, self.bg, self.fg, self.border, self.size = text.upper(), bg, fg, border, size
        self.w = pdfmetrics.stringWidth(self.text, FONT_BODY_BOLD, size) + 16
        self.h = size + 9

    def wrap(self, aw, ah):
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.setStrokeColor(self.border)
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.w, self.h, radius=3, stroke=1, fill=1)
        c.setFillColor(self.fg)
        c.setFont(FONT_BODY_BOLD, self.size)
        c.drawCentredString(self.w / 2, self.h / 2 - self.size * 0.35, self.text)


class PillRow(Flowable):
    def __init__(self, pills, gap=6):
        super().__init__()
        self.pills, self.gap = pills, gap
        self.w = sum(p.w for p in pills) + gap * max(0, len(pills) - 1)
        self.h = max((p.h for p in pills), default=0)

    def wrap(self, aw, ah):
        return self.w, self.h

    def draw(self):
        x = 0
        for p in self.pills:
            p.canv = self.canv
            self.canv.saveState()
            self.canv.translate(x, (self.h - p.h) / 2)
            p.draw()
            self.canv.restoreState()
            x += p.w + self.gap


class CircularProgress(Flowable):
    def __init__(self, value, size=44):
        super().__init__()
        self.value = max(0, min(100, value))
        self.size = size

    def _color(self):
        if self.value >= 80:
            return PALETTE["ring_good"]
        elif self.value >= 50:
            return PALETTE["ring_mid"]
        return PALETTE["ring_low"]

    def wrap(self, aw, ah):
        return self.size, self.size

    def draw(self):
        c = self.canv
        s = self.size
        pen_w = s * 0.13
        r = (s - pen_w) / 2
        cx = cy = s / 2
        c.setLineCap(1)
        c.setLineWidth(pen_w)
        c.setStrokeColor(PALETTE["ring_bg"])
        c.circle(cx, cy, r, stroke=1, fill=0)
        if self.value > 0:
            c.setStrokeColor(self._color())
            p = c.beginPath()
            p.arc(cx - r, cy - r, cx + r, cy + r, 90, -360 * (self.value / 100.0))
            c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(PALETTE["ink"])
        c.setFont(FONT_BODY_BOLD, s * 0.24)
        c.drawCentredString(cx, cy - s * 0.08, f"{self.value}%")


class ChipFlow(Flowable):
    def __init__(self, items, width=None, chip_h=19, h_gap=7, v_gap=7):
        super().__init__()
        self.items = items or []
        self.width_ = width
        self.chip_h, self.h_gap, self.v_gap = chip_h, h_gap, v_gap

    def _chip_w(self, text):
        return pdfmetrics.stringWidth(text, FONT_BODY, 8.6) + 10 + 14

    def wrap(self, aw, ah):
        self._w = self.width_ or aw
        if not self.items:
            self._rows, self._h = [], self.chip_h
            return self._w, self._h
        rows, row, x = [], [], 0.0
        for text in self.items:
            w = self._chip_w(text)
            if row and x + w > self._w:
                rows.append(row)
                row, x = [], 0.0
            row.append((text, x, w))
            x += w + self.h_gap
        if row:
            rows.append(row)
        self._rows = rows
        self._h = len(rows) * self.chip_h + max(0, len(rows) - 1) * self.v_gap
        return self._w, self._h

    def draw(self):
        c = self.canv
        if not self.items:
            c.setFillColor(PALETTE["muted"])
            c.setFont(FONT_BODY_ITALIC, 8.8)
            c.drawString(0, self.chip_h / 2 - 3, "None recorded")
            return
        y = self._h - self.chip_h
        for row in self._rows:
            for text, x, w in row:
                c.setFillColor(PALETTE["chip_bg"])
                c.setStrokeColor(PALETTE["card_border"])
                c.setLineWidth(0.6)
                c.roundRect(x, y, w, self.chip_h, radius=4, stroke=1, fill=1)
                c.setFillColor(PALETTE["success"])
                c.circle(x + 9, y + self.chip_h / 2, 2.3, stroke=0, fill=1)
                c.setFillColor(PALETTE["ink"])
                c.setFont(FONT_BODY, 8.6)
                c.drawString(x + 16, y + self.chip_h / 2 - 3, text)
            y -= (self.chip_h + self.v_gap)


class ProbeBox(Flowable):
    STATE_STYLE = {
        "passed":  dict(border=PALETTE["success_bd"], icon=PALETTE["success"], text=PALETTE["muted_2"], label="PASSED"),
        "probing": dict(border=PALETTE["warning"],     icon=PALETTE["warning"], text=PALETTE["warning"], label="PROBING"),
        "failed":  dict(border=PALETTE["danger"],      icon=PALETTE["danger"],  text=PALETTE["danger"],  label="FAILED"),
        "none":    dict(border=PALETTE["card_border"], icon=PALETTE["muted"],   text=PALETTE["muted"],   label="NOT TESTED"),
    }

    def __init__(self, state, width, height):
        super().__init__()
        self.state = state if state in self.STATE_STYLE else "none"
        self.width_, self.height_ = width, height

    def wrap(self, aw, ah):
        return self.width_, self.height_

    def _icon(self, c, cx, cy, r, color):
        if self.state == "passed":
            _icon_check(c, cx, cy, r, color)
        elif self.state == "failed":
            c.setStrokeColor(color)
            c.setLineWidth(1.4)
            c.setLineCap(1)
            c.line(cx - r, cy - r, cx + r, cy + r)
            c.line(cx - r, cy + r, cx + r, cy - r)
        elif self.state == "probing":
            c.setStrokeColor(color)
            c.setLineWidth(1.2)
            c.circle(cx, cy, r, stroke=1, fill=0)
            p = c.beginPath()
            p.moveTo(cx, cy)
            p.lineTo(cx, cy + r * 0.7)
            c.drawPath(p, stroke=1, fill=0)
            p2 = c.beginPath()
            p2.moveTo(cx, cy)
            p2.lineTo(cx + r * 0.55, cy - r * 0.1)
            c.drawPath(p2, stroke=1, fill=0)
        else:
            c.setStrokeColor(color)
            c.setLineWidth(1.6)
            c.line(cx - r, cy, cx + r, cy)

    def draw(self):
        c = self.canv
        st = self.STATE_STYLE[self.state]
        w, h = self.width_, self.height_
        c.setFillColor(PALETTE["probe_bg"])
        c.setStrokeColor(st["border"])
        c.setLineWidth(0.8)
        c.roundRect(0, 0, w, h, radius=4, stroke=1, fill=1)
        self._icon(c, w / 2, h * 0.62, h * 0.14, st["icon"])
        c.setFillColor(st["text"])
        c.setFont(FONT_BODY_BOLD, 7.6)
        c.drawCentredString(w / 2, h * 0.2, st["label"])


class QuoteBox(Flowable):
    def __init__(self, text, width=None):
        super().__init__()
        self.text, self.width_ = text, width

    def wrap(self, availWidth, availHeight):
        self._w = self.width_ or availWidth
        from reportlab.lib.utils import simpleSplit
        self._lines = simpleSplit(f'\u201c{self.text}\u201d', FONT_BODY_ITALIC, 8.8, self._w - 26)
        self._h = 12 * len(self._lines) + 16
        return self._w, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(PALETTE["quote_bg"])
        c.roundRect(0, 0, self._w, self._h, radius=4, stroke=0, fill=1)
        c.setFillColor(PALETTE["accent"])
        c.roundRect(0, 0, 3, self._h, radius=1.5, stroke=0, fill=1)
        c.setFont(FONT_BODY_ITALIC, 8.8)
        c.setFillColor(PALETTE["muted_2"])
        y = self._h - 13
        for line in self._lines:
            c.drawString(14, y, line)
            y -= 12


class IconTag(Flowable):
    """A small icon + bold uppercase label, used as a panel header."""
    def __init__(self, icon_kind, text, color, size=13):
        super().__init__()
        self.icon_kind, self.text, self.color, self.size = icon_kind, text, color, size
        self.h = size + 2
        self.text_w = pdfmetrics.stringWidth(text.upper(), FONT_BODY_BOLD, 8.8)
        self.w = size + 8 + self.text_w

    def wrap(self, aw, ah):
        return self.w, self.h

    def draw(self):
        c = self.canv
        r = self.size / 2
        ICONS[self.icon_kind](c, r, self.h / 2, r * 0.75, self.color)
        c.setFillColor(self.color)
        c.setFont(FONT_BODY_BOLD, 8.8)
        c.drawString(self.size + 8, self.h / 2 - 3, self.text.upper())


class NumberBadge(Flowable):
    def __init__(self, number, size=22, color=None):
        super().__init__()
        self.number, self.size = number, size
        self.color = color or PALETTE["accent"]

    def wrap(self, aw, ah):
        return self.size, self.size

    def draw(self):
        c = self.canv
        s = self.size
        c.setFillColor(self.color)
        c.circle(s / 2, s / 2, s / 2, stroke=0, fill=1)
        c.setFillColor(PALETTE["page_bg"])
        c.setFont(FONT_BODY_BOLD, s * 0.42)
        c.drawCentredString(s / 2, s / 2 - s * 0.14, str(self.number))


class StatBox(Flowable):
    def __init__(self, value, label, width=None, height=54):
        super().__init__()
        self.value, self.label, self.width_, self.height_ = str(value), label, width, height

    def wrap(self, aw, ah):
        self._w = self.width_ or aw
        return self._w, self.height_

    def draw(self):
        c = self.canv
        c.setFillColor(PALETTE["card_bg"])
        c.setStrokeColor(PALETTE["card_border"])
        c.setLineWidth(0.7)
        c.roundRect(0, 0, self._w, self.height_, radius=6, stroke=1, fill=1)
        c.setFillColor(PALETTE["accent"])
        c.setFont(FONT_DISPLAY_BOLD, 19)
        c.drawCentredString(self._w / 2, self.height_ - 26, self.value)
        c.setFillColor(PALETTE["muted"])
        c.setFont(FONT_BODY, 8)
        c.drawCentredString(self._w / 2, 11, self.label)


def _panel(flowables, bg, accent_bar=None, border=None, width=None, pad=14):
    width = width or INNER_W
    tbl = Table([[flowables]], colWidths=[width])
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if border:
        style.append(("BOX", (0, 0), (-1, -1), 0.7, border))
    if accent_bar:
        style.append(("LINEBEFORE", (0, 0), (0, -1), 3, accent_bar))
    tbl.setStyle(TableStyle(style))
    return tbl


def _bullets(items, color):
    hexv = color.hexval() if hasattr(color, "hexval") else color
    return [Paragraph(f'<font color="{hexv}">\u25CF</font>&nbsp;&nbsp;{text}',
                       styles["Bullet"]) for text in items]


FOOTER_PAGENO_POS = (PAGE_W - MARGIN, 10.5 * mm)

def _draw_cover(c, doc, student_name, report_date):
    c._show_pageno = False
    c.saveState()
    c.setFillColor(PALETTE["page_bg"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#0f1420"))
    c.rect(0, 0, PAGE_W, PAGE_H * 0.58, stroke=0, fill=1)
    c.setFillColor(PALETTE["accent"])
    c.setFillAlpha(0.14)
    p = c.beginPath()
    p.moveTo(0, PAGE_H * 0.58)
    p.lineTo(PAGE_W, PAGE_H * 0.58 + 34)
    p.lineTo(PAGE_W, PAGE_H * 0.58 + 4)
    p.lineTo(0, PAGE_H * 0.58 - 26)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillAlpha(1)
    c.setFillColor(PALETTE["accent"])
    c.setFont(FONT_BODY_BOLD, 10)
    c.drawString(MARGIN, PAGE_H - 55, "FEYNMAN TECHNIQUE  \u00b7  PROGRESS REPORT")
    c.setFillColor(colors.white)
    c.setFont(FONT_DISPLAY_BOLD, 32)
    c.drawString(MARGIN, PAGE_H - 105, "Your Learning")
    c.drawString(MARGIN, PAGE_H - 143, "Progress Report")
    c.setFont(FONT_BODY, 12.5)
    c.setFillColor(colors.HexColor("#b9c4de"))
    c.drawString(MARGIN, PAGE_H - 172, f"Prepared for {student_name}  \u00b7  {report_date}")
    c.setFont(FONT_BODY, 9)
    c.setFillColor(PALETTE["muted"])
    c.drawString(MARGIN, 40, "Generated automatically from your card review history")
    c.restoreState()


def _draw_content_page(c, doc):
    c._show_pageno = True
    c.saveState()
    c.setFillColor(PALETTE["page_bg"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setStrokeColor(PALETTE["hairline"])
    c.setLineWidth(0.6)
    c.line(MARGIN, PAGE_H - 16 * mm, PAGE_W - MARGIN, PAGE_H - 16 * mm)
    c.setFont(FONT_BODY_BOLD, 8.2)
    c.setFillColor(PALETTE["muted"])
    c.drawString(MARGIN, PAGE_H - 13.5 * mm, "FEYNMAN PROGRESS REPORT")
    c.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    c.setFont(FONT_BODY, 8.2)
    c.drawString(MARGIN, 10.5 * mm, "generated report")
    c.restoreState()


class NumberedCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if getattr(self, "_show_pageno", False):
                x, y = FOOTER_PAGENO_POS
                self.setFont(FONT_BODY, 8.2)
                self.setFillColor(PALETTE["muted"])
                self.drawRightString(x, y, f"Page {self._pageNumber} of {total}")
            super().showPage()
        super().save()

def _category_chart(cards):
    totals = {}
    for c in cards:
        totals.setdefault(c["category"], []).append(c["progress"])
    cats = list(totals.keys())
    if not cats:
        return None
    avgs = [sum(v) / len(v) for v in totals.values()]

    longest = max((len(c) for c in cats), default=0)
    angle = 0 if longest <= 12 else 30
    bottom_margin = 34 if angle == 0 else max(34, int(longest * 3.1))
    chart_h = 108 if angle == 0 else 108 + (bottom_margin - 34)
    total_h = chart_h + bottom_margin + 24

    d = Drawing(FRAME_W, total_h)
    d.add(Rect(0, 0, FRAME_W, total_h, fillColor=PALETTE["card_bg"],
               strokeColor=PALETTE["card_border"], strokeWidth=0.7, rx=6, ry=6))

    chart = VerticalBarChart()
    chart.x, chart.y = 42, bottom_margin
    chart.width, chart.height = FRAME_W - 70, chart_h
    chart.data = [avgs]
    chart.categoryAxis.categoryNames = cats
    chart.categoryAxis.labels.fontName = FONT_BODY
    chart.categoryAxis.labels.fontSize = 7.5
    chart.categoryAxis.labels.fillColor = PALETTE["muted_2"]
    chart.categoryAxis.labels.angle = angle
    chart.categoryAxis.strokeColor = PALETTE["hairline"]
    if angle:
        chart.categoryAxis.labels.boxAnchor = "ne"
        chart.categoryAxis.labels.dy = -2
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 25
    chart.valueAxis.labels.fontName = FONT_BODY
    chart.valueAxis.labels.fontSize = 7.5
    chart.valueAxis.labels.fillColor = PALETTE["muted_2"]
    chart.valueAxis.strokeColor = PALETTE["hairline"]
    chart.bars[0].fillColor = PALETTE["accent"]
    chart.barWidth = 14
    chart.groupSpacing = 10
    chart.strokeColor = None
    d.add(chart)
    return d

STATUS_STYLE = {
    "verified":   dict(bg=PALETTE["success_bg"], fg=PALETTE["success"], bd=PALETTE["success_bd"]),
    "wrong":      dict(bg=PALETTE["danger_bg"],  fg=PALETTE["danger"],  bd=PALETTE["danger_bd"]),
    "failed":     dict(bg=PALETTE["danger_bg"],  fg=PALETTE["danger"],  bd=PALETTE["danger_bd"]),
    "unverified": dict(bg=PALETTE["category_bg"], fg=PALETTE["muted_2"], bd=PALETTE["card_border"]),
}

def _card_block(card):
    st = STATUS_STYLE.get(card["status"], STATUS_STYLE["unverified"])
    status_pill = Pill(card["status"], st["bg"], st["fg"], st["bd"])
    category_pill = Pill(card["category"], PALETTE["category_bg"], PALETTE["muted_2"], PALETTE["card_border"])

    ring_size = 46
    header = Table(
        [[[Paragraph(card["name"], styles["CardTitle"]),
           Spacer(1, 6),
           PillRow([status_pill, category_pill])],
          CircularProgress(card["progress"], size=ring_size)]],
        colWidths=[INNER_W - ring_size - 14, ring_size + 14],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    body = [header, Spacer(1, 10)]

    sep = Table([[""]], colWidths=[INNER_W], rowHeights=[1.2])
    sep.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALETTE["hairline"])]))
    body.append(sep)
    body.append(Spacer(1, 12))

    body.append(Paragraph("KEY CONCEPTS", styles["SectionLabel"]))
    body.append(Spacer(1, 6))
    body.append(ChipFlow(card["concepts"], width=INNER_W))
    body.append(Spacer(1, 14))

    body.append(Paragraph("RECENT PROBES", styles["SectionLabel"]))
    body.append(Spacer(1, 6))
    probes = (card["probes"] or [])[-3:]
    probes = (["none"] * (3 - len(probes))) + probes if len(probes) < 3 else probes
    gap = 8
    box_w = (INNER_W - 2 * gap) / 3
    box_h = box_w / 1.75
    probe_row = Table([[ProbeBox(p, box_w, box_h) for p in probes]], colWidths=[box_w] * 3)
    probe_row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (1, 0), (2, 0), gap),
    ]))
    body.append(probe_row)

    dd = card["deep_dive"]
    has_deep_dive = any([dd["whats_working"], dd["root_cause"], dd["fix"]])

    if has_deep_dive:
        body.append(Spacer(1, 14))
        body.append(Paragraph("DEEP DIVE", styles["SectionLabel"]))
        body.append(Spacer(1, 8))

        if dd["whats_working"]:
            body.append(_panel(
                [IconTag("check", "What's working", PALETTE["success"]),
                 Spacer(1, 6),
                 Paragraph(dd["whats_working"], styles["Body"])],
                bg=PALETTE["success_bg"], accent_bar=PALETTE["success"], width=INNER_W))
            body.append(Spacer(1, 8))

        if dd["root_cause"]:
            body.append(_panel(
                [IconTag("alert", "Why the gap exists", PALETTE["warning"]),
                 Spacer(1, 6),
                 Paragraph(dd["root_cause"], styles["Body"])],
                bg=PALETTE["warning_bg"], accent_bar=PALETTE["warning"], width=INNER_W))
            body.append(Spacer(1, 8))

        if dd["fix"]:
            body.append(_panel(
                [IconTag("arrow", "How to close it", PALETTE["accent"]),
                 Spacer(1, 6),
                 Paragraph(dd["fix"], styles["Body"])],
                bg=PALETTE["accent_bg"], accent_bar=PALETTE["accent"], width=INNER_W))
            body.append(Spacer(1, 8))

    elif card["gap"] and card["gap"].lower() not in ("none", "n/a", ""):
        body.append(Spacer(1, 14))
        body.append(_panel(
            [IconTag("alert", "Gap to close", PALETTE["warning"]),
             Spacer(1, 6),
             Paragraph(card["gap"], styles["Body"])],
            bg=PALETTE["warning_bg"], accent_bar=PALETTE["warning"], width=INNER_W))

    if card["quote"]:
        body.append(Spacer(1, 6))
        body.append(Paragraph("IN THEIR OWN WORDS", styles["SectionLabel"]))
        body.append(Spacer(1, 6))
        body.append(QuoteBox(card["quote"], width=INNER_W))

    card_table = Table([[body]], colWidths=[FRAME_W])
    card_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, PALETTE["card_border"]),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("BACKGROUND", (0, 0), (-1, -1), PALETTE["card_bg"]),
    ]))
    return KeepTogether([card_table, Spacer(1, 14)])

def build_feynman_report(cards: list, output_path: str, student_name: str = "Learner",
                          narrative: dict | None = None) -> str:
    """
    Builds the full Feynman progress report PDF and returns the path it was
    saved to.

    `cards` -- raw rows from your `cards_info` table (as dicts). JSON columns
    may be lists or JSON-encoded strings, either works. Each card dict may
    additionally carry a "deep_dive" sub-dict (see module docstring) with
    AI-authored "whats_working" / "root_cause" / "fix" text -- when present,
    it replaces the plain "gap" callout with a full three-panel analysis.

    `narrative` -- optional report-level dict (see module docstring) with
    AI-authored "overview", "strengths", "growth_areas", and "study_plan".
    When omitted, those sections are simply skipped and the report still
    renders cleanly with just the stats, chart, and per-card breakdown.
    """
    from datetime import date
    norm_cards = [_normalize_card(c) for c in cards]
    nar = _normalize_narrative(narrative)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)

    story = [PageBreak()]

    # --- Overview -----------------------------------------------------
    if nar["overview"]:
        story.append(Paragraph("Overview", styles["H1"]))
        story.append(_panel([Paragraph(nar["overview"], styles["Overview"])],
                             bg=PALETTE["card_bg"], accent_bar=PALETTE["accent"],
                             border=PALETTE["card_border"], width=FRAME_W - 30))
        story.append(Spacer(1, 16))

    # --- By the numbers -------------------------------------------------
    story.append(Paragraph("By the Numbers", styles["H1"]))
    total = len(norm_cards)
    avg_progress = round(sum(c["progress"] for c in norm_cards) / total) if total else 0
    verified_count = sum(1 for c in norm_cards if c["status"] == "verified")
    categories = {c["category"] for c in norm_cards}
    stats_row = Table([[
        StatBox(f"{avg_progress}%", "Avg. Progress", width=(FRAME_W - 30) / 4),
        StatBox(total, "Cards Tracked", width=(FRAME_W - 30) / 4),
        StatBox(verified_count, "Verified", width=(FRAME_W - 30) / 4),
        StatBox(len(categories), "Categories", width=(FRAME_W - 30) / 4),
    ]], colWidths=[(FRAME_W - 30) / 4] * 4)
    stats_row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 5),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
    story.append(stats_row)
    story.append(Spacer(1, 18))

    # --- Strengths & growth areas ---------------------------------------
    if nar["strengths"] or nar["growth_areas"]:
        story.append(Paragraph("Strengths & Growth Areas", styles["H1"]))
        gap_w = 16
        col_w = (FRAME_W - gap_w) / 2
        if nar["strengths"]:
            left_content = [IconTag("check", "What's going well", PALETTE["success"]), Spacer(1, 8)]
            left_content += _bullets(nar["strengths"], PALETTE["success"])
            left_panel = _panel(left_content, bg=PALETTE["success_bg"],
                                 accent_bar=PALETTE["success"], width=col_w)
        else:
            left_panel = Spacer(col_w, 1)
        if nar["growth_areas"]:
            right_content = [IconTag("alert", "Where to focus", PALETTE["warning"]), Spacer(1, 8)]
            right_content += _bullets(nar["growth_areas"], PALETTE["warning"])
            right_panel = _panel(right_content, bg=PALETTE["warning_bg"],
                                  accent_bar=PALETTE["warning"], width=col_w)
        else:
            right_panel = Spacer(col_w, 1)
        cols = Table([[left_panel, "", right_panel]], colWidths=[col_w, gap_w, col_w])
        cols.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(cols)
        story.append(Spacer(1, 6))

    # --- Chart ------------------------------------------------------------
    chart = _category_chart(norm_cards)
    if chart:
        story.append(Paragraph("Progress by Category", styles["H1"]))
        story.append(chart)
        story.append(Spacer(1, 6))

    # --- Card-by-card deep dive --------------------------------------------
    story.append(Paragraph("Card-by-Card Deep Dive", styles["H1"]))
    for card in norm_cards:
        story.append(_card_block(card))

    # --- Study plan ------------------------------------------------------
    if nar["study_plan"]:
        story.append(Paragraph("Your Study Plan", styles["H1"]))
        for i, step in enumerate(nar["study_plan"], start=1):
            row = Table([[NumberBadge(i), Paragraph(step, styles["StepText"])]],
                        colWidths=[34, FRAME_W - 34])
            row.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (1, 0), (1, 0), 12),
                ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(row)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title="Feynman Progress Report",
    )
    report_date = date.today().strftime("%B %d, %Y")
    doc.build(
        story,
        onFirstPage=partial(_draw_cover, student_name=student_name, report_date=report_date),
        onLaterPages=_draw_content_page,
        canvasmaker=NumberedCanvas,
    )

    webbrowser.open(output_path)
    return output_path
