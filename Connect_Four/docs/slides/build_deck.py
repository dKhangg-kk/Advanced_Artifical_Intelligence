"""Dựng bộ slide Connect Four (Nhóm 26) từ deck_content.py.

Chạy từ thư mục Connect_Four:
    .venv/bin/python docs/slides/build_deck.py

Tạo ra:
    docs/slides/ConnectFour_Nhom26_Full.pptx
    docs/slides/ConnectFour_Nhom26_ThuyetMinh.md
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Inches, Pt

from deck_content import SLIDES

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT_PPTX = HERE / "ConnectFour_Nhom26_Full.pptx"
OUT_MD = HERE / "ConnectFour_Nhom26_ThuyetMinh.md"
FIGURES = HERE.parents[1] / "results" / "figures"

# --- bảng màu ---------------------------------------------------------------
INK = RGBColor(0x0B, 0x24, 0x2B)
INK_SOFT = RGBColor(0x2C, 0x45, 0x4C)
TEAL = RGBColor(0x2E, 0x7D, 0x8C)
TEAL_DARK = RGBColor(0x12, 0x34, 0x3B)
TEAL_LIGHT = RGBColor(0x8A, 0xA4, 0xAB)
ORANGE = RGBColor(0xE0, 0x7A, 0x2F)
RED = RGBColor(0xB2, 0x3A, 0x48)
GREEN = RGBColor(0x5C, 0x7A, 0x3A)
MUTED = RGBColor(0x6B, 0x8A, 0x90)
GRID = RGBColor(0xDC, 0xE7, 0xE9)
PAPER = RGBColor(0xFB, 0xFD, 0xFD)
PALE = RGBColor(0xEF, 0xF6, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

TITLE_FONT = "Calibri Light"
BODY_FONT = "Calibri"
MONO_FONT = "Consolas"

# Người trình bày gợi ý theo slide (khớp bảng phân công ở slide 02).
SPEAKERS = {
    "Phan Lê Ngọc Như Ý": list(range(14, 22)) + [24, 25, 27],
    "Bùi Quyền Kiệt": [11, 12, 13, 23],
    "Phạm Thái Duy Khang": [3, 4, 8, 9, 10, 22, 26],
    "Bùi Anh Đức": [1, 2, 5, 6, 7, 28, 29],
}
SPEAKER_OF = {n: name for name, nums in SPEAKERS.items() for n in nums}
assert sorted(SPEAKER_OF) == list(range(1, len(SLIDES) + 1)), "phân công chưa đủ 29 slide"

W, H = 13.333, 7.5
MARGIN = 0.75
CONTENT_W = W - 2 * MARGIN


def rgb_hex(color: RGBColor) -> str:
    return str(color)


def set_run(run, size: float, color: RGBColor, bold: bool = False, italic: bool = False, font: str = BODY_FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    run.font.color.rgb = color
    # font cho tiếng Việt / ký tự phức tạp
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = parse_xml(f'<a:ea {nsdecls("a")} typeface="{font}"/>')
        rPr.append(ea)
    cs = rPr.find(qn("a:cs"))
    if cs is None:
        cs = parse_xml(f'<a:cs {nsdecls("a")} typeface="{font}"/>')
        rPr.append(cs)


TOKEN = re.compile(r"(\*\*.+?\*\*|`.+?`)")


def add_runs(paragraph, text: str, size: float, color: RGBColor, bold: bool = False, italic: bool = False, font: str = BODY_FONT):
    for token in TOKEN.split(text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run()
            run.text = token[2:-2]
            set_run(run, size, color, bold=True, italic=italic, font=font)
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run()
            run.text = token[1:-1]
            set_run(run, size * 0.92, TEAL_DARK, bold=bold, italic=False, font=MONO_FONT)
        else:
            run = paragraph.add_run()
            run.text = token
            set_run(run, size, color, bold=bold, italic=italic, font=font)


def bullet_off(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(qn("a:buNone")) is None:
        pPr.append(parse_xml(f'<a:buNone {nsdecls("a")}/>'))


def bullet_on(paragraph, char: str = "▸", color: RGBColor = TEAL, level: int = 0):
    pPr = paragraph._p.get_or_add_pPr()
    marL = 0.30 if level == 0 else 0.66
    indent = -0.30 if level == 0 else -0.22
    pPr.set("marL", str(int(Inches(marL))))
    pPr.set("indent", str(int(Inches(indent))))
    pPr.append(
        parse_xml(
            f'<a:buClr {nsdecls("a")}><a:srgbClr val="{rgb_hex(color)}"/></a:buClr>'
        )
    )
    pPr.append(parse_xml(f'<a:buSzPct {nsdecls("a")} val="90000"/>'))
    pPr.append(parse_xml(f'<a:buFont {nsdecls("a")} typeface="Arial"/>'))
    pPr.append(parse_xml(f'<a:buChar {nsdecls("a")} char="{char}"/>'))


def textbox(slide, x, y, w, h, *, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0)):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (Inches(m) for m in margins)
    tf.clear()
    return box, tf


def paragraph(tf, first: bool):
    if first:
        return tf.paragraphs[0]
    return tf.add_paragraph()


def add_text(
    slide,
    x,
    y,
    w,
    h,
    text,
    *,
    size=18,
    color=INK,
    bold=False,
    italic=False,
    font=BODY_FONT,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    line_spacing=1.0,
):
    box, tf = textbox(slide, x, y, w, h, anchor=anchor)
    for i, line in enumerate(text.split("\n")):
        p = paragraph(tf, i == 0)
        p.alignment = align
        p.line_spacing = line_spacing
        add_runs(p, line, size, color, bold=bold, italic=italic, font=font)
    return box


def add_bullets(slide, x, y, w, h, bullets, *, size=17, color=INK, space_after=9, line_spacing=1.06):
    box, tf = textbox(slide, x, y, w, h)
    for i, item in enumerate(bullets):
        p = paragraph(tf, i == 0)
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        if isinstance(item, dict):
            text = item["text"]
            level = item.get("level", 0)
        else:
            text = item
            level = 0
        if level == 0:
            bullet_on(p, "▸", TEAL, 0)
            add_runs(p, text, size, color)
        else:
            bullet_on(p, "–", TEAL_LIGHT, 1)
            add_runs(p, text, size - 2, INK_SOFT)
    return box


def add_callout(slide, x, y, w, h, text, *, fill=PALE, bar=TEAL, size=14):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.adjustments[0] = 0.10
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    shape.shadow.inherit = False
    bar_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.06), Inches(y + 0.10), Inches(0.07), Inches(h - 0.20))
    bar_shape.fill.solid()
    bar_shape.fill.fore_color.rgb = bar
    bar_shape.line.fill.background()
    bar_shape.shadow.inherit = False
    box, tf = textbox(slide, x + 0.26, y + 0.04, w - 0.40, h - 0.08, anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]
    p.line_spacing = 1.02
    add_runs(p, text, size, INK)


def asset(name: str) -> Path:
    path = ASSETS / name
    if path.exists():
        return path
    path = FIGURES / name
    if path.exists():
        return path
    raise FileNotFoundError(name)


def add_picture_fit(slide, path: Path, x, y, w, h):
    with Image.open(path) as im:
        aspect = im.width / im.height
    iw, ih = w, w / aspect
    if ih > h:
        ih, iw = h, h * aspect
    left = x + (w - iw) / 2
    top = y + (h - ih) / 2
    slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(iw), Inches(ih))
    return left, top, iw, ih


def add_caption(slide, x, y, w, text):
    add_text(slide, x, y, w, 0.34, text, size=10.5, color=MUTED, italic=True, align=PP_ALIGN.CENTER)


def add_footer(slide, number: int):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(7.04), Inches(CONTENT_W), Inches(0.012))
    line.fill.solid()
    line.fill.fore_color.rgb = GRID
    line.line.fill.background()
    line.shadow.inherit = False
    add_text(slide, MARGIN, 7.09, 6.5, 0.26, "Connect Four AI · Nhóm 26", size=9, color=MUTED)
    add_text(slide, W - MARGIN - 1.0, 7.09, 1.0, 0.26, f"{number:02d}", size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def add_header(slide, part: str, title: str, kicker: str | None):
    add_text(slide, MARGIN, 0.34, CONTENT_W, 0.28, part, size=10.5, color=TEAL, bold=True)
    size = 29 if len(title) <= 44 else (26 if len(title) <= 54 else 23)
    add_text(slide, MARGIN, 0.62, CONTENT_W, 0.86, title, size=size, color=INK, bold=True, font=TITLE_FONT, line_spacing=0.95)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(MARGIN), Inches(1.50), Inches(0.92), Inches(0.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()
    bar.shadow.inherit = False
    if kicker:
        add_text(slide, MARGIN, 1.60, CONTENT_W, 0.40, kicker, size=14, color=TEAL_DARK, italic=True)
    return 2.12 if kicker else 1.78


def add_table(slide, spec, y):
    headers = spec["headers"]
    rows = spec["rows"]
    widths = spec["widths"]
    font = spec.get("font", 13)
    row_h = spec.get("row_height", 0.50)
    header_h = spec.get("header_height", 0.44)
    total_w = sum(widths)
    height = header_h + row_h * len(rows)
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(MARGIN), Inches(y), Inches(total_w), Inches(height))
    table = shape.table
    table.first_row = False
    table.horz_banding = False
    # "No Style, No Grid"
    tbl = table._tbl
    tblPr = tbl.tblPr
    style = tblPr.find(qn("a:tableStyleId"))
    if style is None:
        style = parse_xml(f'<a:tableStyleId {nsdecls("a")}>{{2D5ABB26-0587-4C30-8999-92F81FD0307C}}</a:tableStyleId>')
        tblPr.append(style)
    else:
        style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"

    for idx, width in enumerate(widths):
        table.columns[idx].width = Inches(width)
    table.rows[0].height = Inches(header_h)
    for r in range(1, len(rows) + 1):
        table.rows[r].height = Inches(row_h)

    for c, head in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = TEAL_DARK
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.10)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        add_runs(p, head, font, WHITE, bold=True)

    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r % 2 else PALE
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.10)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            add_runs(p, value, font, INK, bold=(c == 0))
            # đường kẻ dưới mảnh
            tcPr = cell._tc.get_or_add_tcPr()
            if tcPr.find(qn("a:lnB")) is None:
                tcPr.append(
                    parse_xml(
                        f'<a:lnB {nsdecls("a")} w="9525"><a:solidFill><a:srgbClr val="{rgb_hex(GRID)}"/></a:solidFill></a:lnB>'
                    )
                )
    return y + height


def add_cards(slide, cards, y):
    gap = 0.30
    card_w = (CONTENT_W - gap) / 2
    card_h = 1.42
    for i, card in enumerate(cards):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (card_w + gap)
        top = y + row * (card_h + 0.22)
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(top), Inches(card_w), Inches(card_h))
        shape.adjustments[0] = 0.08
        shape.fill.solid()
        shape.fill.fore_color.rgb = PALE
        shape.line.fill.background()
        shape.shadow.inherit = False
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + 0.05), Inches(top + 0.12), Inches(0.06), Inches(card_h - 0.24))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ORANGE if card["label"] == "RQ3" else TEAL
        bar.line.fill.background()
        bar.shadow.inherit = False
        add_text(slide, x + 0.24, top + 0.13, 1.0, 0.28, card["label"], size=12.5, color=TEAL, bold=True)
        add_text(slide, x + 0.24, top + 0.40, card_w - 0.45, card_h - 0.50, card["text"], size=12.8, color=INK, line_spacing=1.02)


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    blank = prs.slide_layouts[6]

    for index, spec in enumerate(SLIDES, start=1):
        kind = spec["kind"]
        slide = prs.slides.add_slide(blank)

        if kind == "title":
            bg = slide.background.fill
            bg.solid()
            bg.fore_color.rgb = INK
            slide.shapes.add_picture(str(ASSETS / "hero_board.png"), 0, 0, Inches(W), Inches(H))
            add_text(slide, 0.80, 1.28, 5.4, 0.30, "ĐỒ ÁN CUỐI KỲ · TRÍ TUỆ NHÂN TẠO NÂNG CAO", size=10.5, color=TEAL_LIGHT, bold=True)
            add_text(slide, 0.80, 1.62, 5.5, 1.0, spec["title"], size=44, color=WHITE, bold=True, font=TITLE_FONT)
            add_text(slide, 0.80, 2.62, 5.4, 0.80, spec["subtitle"], size=19, color=RGBColor(0xCF, 0xE0, 0xE3), line_spacing=1.05)
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.82), Inches(3.55), Inches(1.1), Inches(0.045))
            line.fill.solid()
            line.fill.fore_color.rgb = ORANGE
            line.line.fill.background()
            line.shadow.inherit = False
            add_text(slide, 0.80, 3.72, 5.2, 0.85, "\n".join(spec["meta"]), size=11.5, color=RGBColor(0xE8, 0xF1, 0xF2), line_spacing=1.35)
            add_text(slide, 0.80, 4.78, 5.3, 1.5, "\n".join(spec["members"]), size=10.5, color=TEAL_LIGHT, line_spacing=1.45)
            add_text(slide, 0.80, 6.72, 5.3, 0.28, "Nhóm 26 · 11/2026", size=9, color=RGBColor(0x7F, 0x9B, 0xA2))
            slide.notes_slide.notes_text_frame.text = spec["notes"]
            continue

        if kind == "closing":
            bg = slide.background.fill
            bg.solid()
            bg.fore_color.rgb = TEAL_DARK
            for cx, cy, d, color in [(12.3, 1.2, 1.9, RGBColor(0x1B, 0x4A, 0x54)), (0.6, 6.4, 1.4, RGBColor(0x6B, 0x4A, 0x2C))]:
                disc = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
                disc.fill.solid()
                disc.fill.fore_color.rgb = color
                disc.line.fill.background()
                disc.shadow.inherit = False
            add_text(slide, 1.0, 2.15, 11.3, 0.9, spec["title"], size=38, color=WHITE, bold=True, font=TITLE_FONT, align=PP_ALIGN.CENTER)
            add_text(slide, 1.0, 3.20, 11.3, 0.6, spec["subtitle"], size=20, color=RGBColor(0xCF, 0xE0, 0xE3), align=PP_ALIGN.CENTER)
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.17), Inches(3.98), Inches(1.0), Inches(0.045))
            bar.fill.solid()
            bar.fill.fore_color.rgb = ORANGE
            bar.line.fill.background()
            bar.shadow.inherit = False
            add_text(slide, 1.0, 4.35, 11.3, 0.8, "\n".join(spec["meta"]), size=11.5, color=TEAL_LIGHT, align=PP_ALIGN.CENTER, line_spacing=1.4)
            slide.notes_slide.notes_text_frame.text = spec["notes"]
            continue

        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = PAPER
        top = add_header(slide, spec["part"], spec["title"], spec.get("kicker"))

        layout = spec["layout"]
        if layout == "bullets":
            bottom = 6.92
            if spec.get("callout"):
                add_callout(slide, MARGIN, 6.02, CONTENT_W, 0.78, spec["callout"])
                bottom = 5.85
            size = 17 if len(spec["bullets"]) <= 5 else 16
            add_bullets(slide, MARGIN, top, CONTENT_W, bottom - top, spec["bullets"], size=size)
        elif layout == "image-right":
            add_bullets(slide, MARGIN, top, 5.55, 4.95, spec["bullets"], size=15.5)
            box = (6.52, top - 0.02, 6.06, 4.55)
            _, _, _, ih = add_picture_fit(slide, asset(spec["image"]), *box)
            if spec.get("image_caption"):
                add_caption(slide, box[0], top + 4.62, box[2], spec["image_caption"])
        elif layout == "image-full":
            add_bullets(slide, MARGIN, top, CONTENT_W, 1.10, spec["bullets"], size=14.5, space_after=4)
            add_picture_fit(slide, asset(spec["image"]), MARGIN, 2.98, CONTENT_W, 3.88)
        elif layout == "table":
            bottom = add_table(slide, spec["table"], top)
            add_bullets(slide, MARGIN, bottom + 0.26, CONTENT_W, 6.95 - bottom - 0.26, spec["bullets"], size=14.5, space_after=6)
            if spec.get("callout"):
                add_callout(slide, MARGIN, 6.10, CONTENT_W, 0.72, spec["callout"], size=13)
        elif layout == "cards":
            add_bullets(slide, MARGIN, top, CONTENT_W, 0.80, spec["bullets"], size=14.5, space_after=3)
            add_cards(slide, spec["cards"], top + 0.92)
        elif layout == "two-images":
            add_bullets(slide, MARGIN, top, CONTENT_W, 0.95, spec["bullets"], size=14, space_after=3)
            box_w = 5.25
            for i, (image, caption) in enumerate(zip(spec["images"], spec["captions"])):
                x = MARGIN + i * (box_w + 0.85)
                _, _, _, ih = add_picture_fit(slide, asset(image), x, 2.86, box_w, 3.12)
                add_caption(slide, x, 6.06, box_w, caption)
        else:
            raise ValueError(f"layout lạ: {layout}")

        add_footer(slide, index)
        slide.notes_slide.notes_text_frame.text = spec["notes"]

    prs.core_properties.title = "Connect Four AI — Sáu cấp tác tử"
    prs.core_properties.author = "Nhóm 26 — Phan Lê Ngọc Như Ý, Bùi Quyền Kiệt, Phạm Thái Duy Khang, Bùi Anh Đức"
    prs.core_properties.subject = "Đồ án cuối kỳ Trí tuệ nhân tạo nâng cao"
    prs.core_properties.keywords = "Connect Four, Alpha-Beta, MCTS, CNN, DQN, ablation"
    prs.save(OUT_PPTX)
    print("wrote", OUT_PPTX)


def strip_md(text: str) -> str:
    text = text.replace("**", "")
    return text.replace("`", "")


def mmss(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def build_md():
    total = sum(s["time"] for s in SLIDES)
    lines = [
        "# Connect Four AI — Thuyết minh bộ slide",
        "",
        "**Nhóm 26 · Trường Đại học Sài Gòn · Trí tuệ nhân tạo nâng cao · GV: Đỗ Như Tài**",
        "",
        f"Tổng thời lượng gợi ý: **{mmss(total)}** cho 29 slide. Bản rút gọn 15 phút: bỏ slide 6, 12, 15, 20 và đọc lướt 22–25.",
        "",
        "> Cách dùng: mỗi mục dưới đây tương ứng một slide. Phần “Nội dung trên slide” là chữ đã có trên màn hình; "
        "phần “Thuyết minh” là lời nói gợi ý, có thể đọc gần như nguyên văn. Các con số đều lấy từ "
        "`results/tables/` và `docs/report/`.",
        "",
        "---",
        "",
    ]
    for i, s in enumerate(SLIDES, start=1):
        title = s["title"]
        lines.append(f"## Slide {i:02d} — {title}  ·  {mmss(s['time'])}")
        lines.append("")
        lines.append(f"**Người trình bày:** {SPEAKER_OF[i]}")
        lines.append("")
        if s.get("part"):
            lines.append(f"**Phần:** {s['part']}")
            lines.append("")
        if s.get("kicker"):
            lines.append(f"*{strip_md(s['kicker'])}*")
            lines.append("")
        if s["kind"] == "title":
            lines.append(f"**Phụ đề:** {s['subtitle']}")
            lines.append("")
            lines.append("**Trên slide:**")
            for m in s["meta"] + s["members"]:
                lines.append(f"- {m}")
            lines.append("")
        if s["kind"] == "closing":
            lines.append(f"**Phụ đề:** {s['subtitle']}")
            lines.append("")
            for m in s["meta"]:
                lines.append(f"- {m}")
            lines.append("")
        if s.get("bullets"):
            lines.append("**Nội dung trên slide:**")
            lines.append("")
            for b in s["bullets"]:
                text = b["text"] if isinstance(b, dict) else b
                lines.append(f"- {strip_md(text)}")
            lines.append("")
        if s.get("table"):
            t = s["table"]
            lines.append("| " + " | ".join(t["headers"]) + " |")
            lines.append("|" + "|".join(["---"] * len(t["headers"])) + "|")
            for row in t["rows"]:
                lines.append("| " + " | ".join(strip_md(c) for c in row) + " |")
            lines.append("")
        if s.get("cards"):
            for card in s["cards"]:
                lines.append(f"- **{card['label']}:** {strip_md(card['text'])}")
            lines.append("")
        if s.get("image"):
            lines.append(f"**Hình:** `docs/slides/assets/{s['image']}`")
            if s.get("image_caption"):
                lines.append(f"*{strip_md(s['image_caption'])}*")
            lines.append("")
        if s.get("images"):
            for img, cap in zip(s["images"], s["captions"]):
                lines.append(f"**Hình:** `docs/slides/assets/{img}` — {strip_md(cap)}")
            lines.append("")
        if s.get("callout"):
            lines.append(f"> **Thông điệp:** {strip_md(s['callout'])}")
            lines.append("")
        lines.append("**Thuyết minh:**")
        lines.append("")
        for para in s["notes"].split("\n\n"):
            lines.append(para.strip())
            lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "## Phụ lục — nguồn số liệu",
        "",
        "| Nội dung | Tệp |",
        "| --- | --- |",
        "| Điểm, độ trễ, ma trận | `results/tables/y6_default_agent_summary.csv`, `y6_timed_agent_summary.csv`, `y6_default_score_matrix.csv` |",
        "| Độ đúng chiến thuật | `results/tables/y6_position_accuracy.csv` |",
        "| Lợi thế đi trước | `results/tables/y6_default_first_move.csv`, `y6_timed_first_move.csv` |",
        "| Ablation tìm kiếm | `results/tables/ablation_a1_results.csv`, `ablation_a2_results.csv`, `ablation_a5_results.csv` |",
        "| Ablation CNN | `results/tables/ablation_a3_results.csv` |",
        "| Ablation DQN | `results/tables/ablation_a4_summary.csv`, `ablation_a6_pooled.csv` |",
        "| Chẩn đoán DQN | `results/tables/dqn_opening_diagnostic.csv` |",
        "| Số liệu đã đối chiếu | `results/tables/report_numbers.csv` |",
        "",
        "### Lịch trình gợi ý",
        "",
        "| Phần | Slide | Thời lượng |",
        "| --- | --- | ---: |",
    ]
    for label, lo, hi in [
        ("Mở đầu & nền tảng", 1, 7),
        ("Sáu tác tử", 8, 15),
        ("Giải đấu & kết quả", 16, 21),
        ("Phân tích & kết luận", 22, 29),
    ]:
        lines.append(f"| {label} | {lo}–{hi} | {mmss(sum(SLIDES[i]['time'] for i in range(lo - 1, hi)))} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT_MD)


if __name__ == "__main__":
    build_pptx()
    build_md()
