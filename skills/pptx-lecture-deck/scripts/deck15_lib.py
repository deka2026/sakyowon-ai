# -*- coding: utf-8 -*-
"""Conference deck renderer with a minimum body font (default 15pt) and Korean/English modes.

Generalized from the 2026-09 Jeonnam-Gwangju conference deck (19 slides, KO + EN).
Differences from deck_lib.slide_question:
  * body font is chosen per slide from CANDS (17 -> 16 -> 15); never below MIN
  * card headings may wrap; bullets start below the measured heading height
  * language mode sets the font and the per-character width used by the line estimator
    (Korean 0.88 em, English 0.55 em) -- English needs ~25% shorter sentences
  * optional footer (source note); the submitted Korean deck omitted it
  * table / flow / title / agenda / closing slide types

Usage:
    import deck15_lib as D
    D.configure(lang="ko")                 # or "en"; sets deck_lib.FONT too
    prs = D.new_deck()
    D.slide_cards(prs, 1, "title", "lead", [[("heading", ["bullet", "*bold bullet"])], [...]], footer="source")
    D.slide_table(prs, 6, "title", "lead", ["Item", "A", "B"], [["r", "a", "b"]], [1.9, 4.75, 5.58])
    D.slide_flow(prs, 8, "title", "lead", [("1", "head", ["b1", "b2"]), ...], "formula", "sub")
    D.slide_closing(prs, "msg", "sub", ["line", ...])
    prs.save(out)
The console prints "slide NN: font 15.0  OVERFLOW" when the estimate does not fit; the estimate is
conservative for English, so confirm with export_png.ps1 and the Read tool before trimming text.
"""
import math
import deck_lib
from deck_lib import (new_deck, blank, para, rect, textbox, Inches, RGBColor, PP_ALIGN, MSO_SHAPE,
                      DARK, MID, LIGHT, LIME, INK, GRAY, WHITE, CARDBG, LINE, WARN,
                      SW, SH, MARGIN, BODY_W, BODY_TOP, CARD_GAP, COL_GAP)
from pptx.enum.text import MSO_ANCHOR

AMBER = RGBColor(0xE0, 0x9F, 0x3E)
MIN = 15.0
CANDS = (17.0, 16.0, 15.0)
CFG = {"lang": "ko", "char_w": 0.88}


def configure(lang="ko", min_size=15.0, cands=(17.0, 16.0, 15.0), font=None):
    """lang: 'ko' (맑은 고딕, 0.88 em/char) or 'en' (Calibri, 0.55 em/char)."""
    global MIN, CANDS
    MIN, CANDS = float(min_size), tuple(cands)
    CFG["lang"] = lang
    CFG["char_w"] = 0.88 if lang == "ko" else 0.55
    deck_lib.FONT = font or ("맑은 고딕" if lang == "ko" else "Calibri")


def est_lines(text, size, width_in):
    char_w = size * CFG["char_w"] / 72.0
    per_line = max(8, int(width_in / char_w))
    return max(1, math.ceil(len(text) / per_line))


def header(s, num, title, lead):
    rect(s, 0, 0, SW, 1.12, fill=DARK)
    rect(s, MARGIN, 0.24, 0.66, 0.64, fill=LIME)
    tb = textbox(s, MARGIN, 0.30, 0.66, 0.56)
    para(tb.text_frame, f"{num:02d}", size=17, bold=True, color=DARK, first=True, align=PP_ALIGN.CENTER)
    tb = textbox(s, 1.42, 0.14, 11.4, 0.92)
    tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    long_title = len(title) > (62 if CFG["lang"] == "en" else 34)
    para(tb.text_frame, title, size=22 if long_title else 24, bold=True, color=WHITE, first=True, line=1.0)
    rect(s, 0, 1.12, SW, 0.78, fill=LIGHT)
    rect(s, 0, 1.12, 0.12, 0.78, fill=MID)
    tb = textbox(s, MARGIN, 1.14, 12.3, 0.74)
    tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    long_lead = len(lead) > (105 if CFG["lang"] == "en" else 60)
    para(tb.text_frame, lead, size=MIN if long_lead else 16, bold=True, color=DARK, first=True, line=1.08)


def footer(s, note):
    rect(s, MARGIN, 6.92, BODY_W, 0.03, fill=LINE)
    tb = textbox(s, MARGIN, 6.96, BODY_W, 0.45)
    para(tb.text_frame, note, size=MIN, color=GRAY, first=True)


def card_h(heading, bullets, size, cw):
    tw = cw - 0.42
    hs = size + 2.5
    h = 0.16 + est_lines(heading, hs, cw - 0.4) * (hs * 1.20 / 72.0) + 0.15
    for b in bullets:
        t = b[1:] if b.startswith("*") else b
        h += est_lines("> " + t, size, tw) * (size * 1.22 / 72.0) + 5.0 / 72.0
    return h + 0.22


def slide_cards(prs, num, title, lead, cols, footer_note=None):
    """cols: list of columns; column = list of (heading, [bullets]); bullet starting with '*' is bold."""
    s = blank(prs)
    header(s, num, title, lead)
    top, bottom = BODY_TOP, (6.85 if footer_note else 7.08)
    n = len(cols)
    cw = (BODY_W - COL_GAP * (n - 1)) / n
    size = CANDS[-1]
    for cand in CANDS:
        if all(sum(card_h(h, b, cand, cw) for h, b in col) + CARD_GAP * (len(col) - 1) <= bottom - top for col in cols):
            size = cand
            break
    x = MARGIN
    overflow = False
    for col in cols:
        avail = (bottom - top) - CARD_GAP * (len(col) - 1)
        needs = [card_h(h, b, size, cw) for h, b in col]
        tot = sum(needs)
        if tot > avail:
            overflow = True
            heights = [nd * avail / tot for nd in needs]
        else:
            heights = [nd + (avail - tot) * (nd / tot) for nd in needs]
        y = top
        for (heading, bullets), h in zip(col, heights):
            rect(s, x, y, cw, h, fill=CARDBG, line_color=LINE)
            rect(s, x, y, cw, 0.05, fill=MID)
            hs = size + 2.5
            hl = est_lines(heading, hs, cw - 0.4)
            tb = textbox(s, x + 0.2, y + 0.11, cw - 0.4, hl * hs * 1.20 / 72.0 + 0.1)
            para(tb.text_frame, heading, size=hs, bold=True, color=DARK, first=True, line=1.1)
            tb = textbox(s, x + 0.2, y + 0.11 + hl * hs * 1.20 / 72.0 + 0.13, cw - 0.38, h - 0.4)
            tf = tb.text_frame
            for i, b in enumerate(bullets):
                strong = b.startswith("*")
                para(tf, b[1:] if strong else b, size=size, color=DARK if strong else INK, bold=strong,
                     first=(i == 0), space_after=5, bullet="▸", line=1.2)
            y += h + CARD_GAP
        x += cw + COL_GAP
    if footer_note:
        footer(s, footer_note)
    print(f"slide {num:02d}: font {size}{'  OVERFLOW' if overflow else ''}")
    return s


def slide_table(prs, num, title, lead, header_row, rows, widths, note=None, footer_note=None):
    """3-column comparison table. widths in inches (sum ~= BODY_W). note: optional amber callout under the table."""
    s = blank(prs)
    header(s, num, title, lead)
    top = 2.10
    bottom = (6.85 if footer_note else 7.05) - (0.50 if note else 0)
    size = MIN

    def row_h(cells, sz):
        return max(est_lines(c, sz, w - 0.22) for c, w in zip(cells, widths)) * (sz * 1.25 / 72.0) + 0.18
    hh = 0.50
    for cand in CANDS:
        hs = [row_h(r, cand) for r in rows]
        if hh + sum(hs) <= bottom - top:
            size = cand
            break
    hs = [row_h(r, size) for r in rows]
    avail = bottom - top - hh
    tot = sum(hs)
    print(f"slide {num:02d} table: font {size}{'  OVERFLOW' if tot > avail else ''}")
    hs = [h * avail / tot for h in hs]
    x = MARGIN
    for c, w, col in zip(header_row, widths, (DARK, GRAY, MID)):
        rect(s, x, top, w, hh, fill=col, line_color=WHITE, line_w=1)
        tb = textbox(s, x, top + 0.09, w, hh)
        para(tb.text_frame, c, size=size + 1, bold=True, color=WHITE, first=True, align=PP_ALIGN.CENTER)
        x += w
    y = top + hh
    for ri, (r, h) in enumerate(zip(rows, hs)):
        x = MARGIN
        for ci, (c, w) in enumerate(zip(r, widths)):
            if ci == 0:
                fill, col, bold = LIGHT, DARK, True
            elif ci == 1:
                fill, col, bold = (WHITE if ri % 2 else CARDBG), INK, False
            else:
                fill, col, bold = RGBColor(0xEE, 0xF6, 0xF2) if ri % 2 else RGBColor(0xE4, 0xF1, 0xEA), DARK, False
            rect(s, x, y, w, h, fill=fill, line_color=WHITE, line_w=1)
            tb = textbox(s, x + 0.08, y + 0.04, w - 0.16, h - 0.06)
            tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            para(tb.text_frame, c, size=size, bold=bold, color=col, first=True, line=1.18,
                 align=PP_ALIGN.CENTER if ci == 0 else PP_ALIGN.LEFT)
            x += w
        y += h
    if note:
        rect(s, MARGIN, y + 0.08, BODY_W, 0.42, fill=RGBColor(0xFB, 0xF0, 0xE8))
        rect(s, MARGIN, y + 0.08, 0.08, 0.42, fill=AMBER)
        tb = textbox(s, MARGIN + 0.15, y + 0.12, BODY_W - 0.2, 0.38)
        para(tb.text_frame, note, size=MIN, bold=True, color=WARN, first=True)
    if footer_note:
        footer(s, footer_note)
    return s


def slide_flow(prs, num, title, lead, boxes, formula, sub, loop_text=None, footer_note=None):
    """boxes: list of (label, head, [bullets]) rendered left-to-right with arrows; last box is dark."""
    s = blank(prs)
    header(s, num, title, lead)
    n = len(boxes)
    gap = 0.42
    bw = (BODY_W - gap * (n - 1)) / n
    top, bh = 2.15, 3.1
    x = MARGIN
    for i, (lbl, head, bullets) in enumerate(boxes):
        rect(s, x, top, bw, bh, fill=CARDBG, line_color=LINE)
        rect(s, x, top, bw, 0.95, fill=MID if i < n - 1 else DARK)
        tb = textbox(s, x + 0.12, top + 0.06, bw - 0.24, 0.88)
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        para(tb.text_frame, f"{lbl} {head}", size=16, bold=True, color=WHITE, first=True, line=1.05)
        tb = textbox(s, x + 0.15, top + 1.05, bw - 0.3, bh - 1.1)
        tf = tb.text_frame
        for j, b in enumerate(bullets):
            para(tf, b, size=MIN, color=INK, first=(j == 0), bullet="▸", space_after=6, line=1.18)
        if i < n - 1:
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw + 0.05), Inches(top + bh / 2 - 0.2),
                                    Inches(gap - 0.1), Inches(0.4))
            ar.fill.solid(); ar.fill.fore_color.rgb = LIME; ar.line.fill.background(); ar.shadow.inherit = False
        x += bw + gap
    y = top + bh + 0.12
    if loop_text:
        rect(s, MARGIN, y, BODY_W, 0.46, fill=LIGHT)
        tb = textbox(s, MARGIN, y + 0.05, BODY_W, 0.4)
        para(tb.text_frame, loop_text, size=MIN, bold=True, color=DARK, first=True, align=PP_ALIGN.CENTER)
        y += 0.60
    rect(s, MARGIN, y, BODY_W, 0.62, fill=DARK)
    tb = textbox(s, MARGIN, y + 0.10, BODY_W, 0.5)
    para(tb.text_frame, formula, size=18, bold=True, color=LIME, first=True, align=PP_ALIGN.CENTER)
    tb = textbox(s, MARGIN, y + 0.66, BODY_W, 0.4)
    para(tb.text_frame, sub, size=MIN, color=GRAY, first=True, align=PP_ALIGN.CENTER)
    if footer_note:
        footer(s, footer_note)
    return s


def slide_title(prs, kicker_lines, title, subtitle, tagline, extra_line, when_where, presenter, note):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=DARK)
    rect(s, 0, 5.55, SW, 1.95, fill=MID)
    rect(s, MARGIN, 0.55, 0.14, 1.05, fill=LIME)
    tb = textbox(s, 0.85, 0.50, 11.8, 1.1)
    for i, k in enumerate(kicker_lines):
        para(tb.text_frame, k, size=15, color=LIGHT, first=(i == 0))
    tb = textbox(s, MARGIN, 1.85, 12.2, 1.3)
    para(tb.text_frame, title, size=34 if len(title) > 24 else 38, bold=True, color=WHITE, first=True, line=1.05)
    tb = textbox(s, MARGIN, 3.05, 12.2, 2.4)
    para(tb.text_frame, subtitle, size=20, bold=True, color=LIME, first=True, line=1.1)
    para(tb.text_frame, tagline, size=18, color=LIGHT, space_before=6)
    if extra_line:
        para(tb.text_frame, extra_line, size=15, color=LIGHT, space_before=8, line=1.15)
    tb = textbox(s, MARGIN, 5.75, 12.2, 1.6)
    para(tb.text_frame, when_where, size=16, bold=True, color=WHITE, first=True)
    para(tb.text_frame, presenter, size=16, color=WHITE, space_before=4)
    para(tb.text_frame, note, size=15, color=LIGHT, space_before=8)
    return s


def slide_agenda(prs, title, items, box_title, box_bullets):
    """items: list of (range_label, heading, description)."""
    s = blank(prs)
    rect(s, 0, 0, SW, 1.12, fill=DARK)
    tb = textbox(s, MARGIN, 0.22, 12.2, 0.75)
    tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tb.text_frame, title, size=24, bold=True, color=WHITE, first=True)
    y = 1.40
    for n, t, d in items:
        rect(s, MARGIN, y, 1.35, 0.92, fill=MID)
        tb = textbox(s, MARGIN, y + 0.24, 1.35, 0.5)
        para(tb.text_frame, n, size=16, bold=True, color=WHITE, first=True, align=PP_ALIGN.CENTER)
        rect(s, MARGIN + 1.35, y, 7.0, 0.92, fill=CARDBG, line_color=LINE)
        tb = textbox(s, MARGIN + 1.55, y + 0.07, 6.7, 0.85)
        para(tb.text_frame, t, size=17, bold=True, color=DARK, first=True, space_after=1)
        para(tb.text_frame, d, size=15, color=INK)
        y += 1.06
    rect(s, 9.15, 1.40, 3.63, 5.22, fill=LIGHT)
    rect(s, 9.15, 1.40, 3.63, 0.06, fill=AMBER)
    tb = textbox(s, 9.33, 1.58, 3.3, 5.0)
    tf = tb.text_frame
    para(tf, box_title, size=17, bold=True, color=DARK, first=True, space_after=8)
    for b in box_bullets:
        para(tf, b, size=15, color=INK, bullet="▸", space_after=7, line=1.18)
    return s


def slide_closing(prs, msg, sub, lines, thanks="감사합니다  |  Thank you"):
    s = blank(prs)
    rect(s, 0, 0, SW, SH, fill=DARK)
    rect(s, MARGIN, 0.95, 0.14, 1.6, fill=LIME)
    tb = textbox(s, 0.9, 0.85, 11.9, 2.1)
    para(tb.text_frame, msg, size=28, bold=True, color=WHITE, first=True, line=1.15)
    para(tb.text_frame, sub, size=16, color=LIGHT, space_before=10, line=1.2)
    rect(s, MARGIN, 3.45, BODY_W, 0.03, fill=MID)
    tb = textbox(s, MARGIN, 3.65, BODY_W, 3.0)
    tf = tb.text_frame
    for i, l in enumerate(lines):
        para(tf, l, size=16, color=LIGHT, first=(i == 0), bullet="▸", space_after=12, line=1.25)
    tb = textbox(s, MARGIN, 6.75, BODY_W, 0.5)
    para(tb.text_frame, thanks, size=16, bold=True, color=LIME, first=True, align=PP_ALIGN.RIGHT)
    return s
