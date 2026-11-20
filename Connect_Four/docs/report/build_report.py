"""Build the available ordered Markdown report sections into a DOCX draft."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "report"
DIST = REPORT / "dist"
OUTPUT = DIST / "BaoCao_CuoiKy_Nhom26_ban_nhanh.docx"  # ban day du: build_docx_pdf.py


def clean_inline(text: str) -> str:
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    return text.replace("\\|", "|").strip()


def is_table_separator(line: str) -> bool:
    cells = [part.strip() for part in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def add_markdown_table(document: Document, lines: list[str]) -> None:
    rows = [
        [clean_inline(cell) for cell in line.strip().strip("|").split("|")]
        for line in lines
        if not is_table_separator(line)
    ]
    if not rows:
        return
    columns = max(map(len, rows))
    table = document.add_table(rows=0, cols=columns)
    table.style = "Light Shading Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index in range(columns):
            cell = cells[index]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = values[index] if index < len(values) else ""
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8.5)
                    if row_index == 0:
                        run.bold = True
    document.add_paragraph()


def add_markdown(document: Document, source: Path) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    index = 0
    in_code = False
    code_lines: list[str] = []
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.left_indent = Inches(0.25)
                run = paragraph.add_run("\n".join(code_lines))
                run.font.name = "Consolas"
                run.font.size = Pt(8)
                code_lines = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not stripped:
            index += 1
            continue
        if stripped.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            add_markdown_table(document, table_lines)
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = min(len(heading.group(1)), 4)
            document.add_heading(clean_inline(heading.group(2)), level=level)
        elif stripped.startswith(">"):
            paragraph = document.add_paragraph(style="Quote")
            paragraph.add_run(clean_inline(stripped.lstrip("> ")))
        elif re.match(r"^[-*+]\s+", stripped):
            document.add_paragraph(clean_inline(re.sub(r"^[-*+]\s+", "", stripped)), style="List Bullet")
        elif re.match(r"^\d+[.)]\s+", stripped):
            document.add_paragraph(clean_inline(re.sub(r"^\d+[.)]\s+", "", stripped)), style="List Number")
        else:
            document.add_paragraph(clean_inline(stripped))
        index += 1
    if in_code and code_lines:
        paragraph = document.add_paragraph()
        run = paragraph.add_run("\n".join(code_lines))
        run.font.name = "Consolas"
        run.font.size = Pt(8)


def main() -> int:
    order_file = REPORT / "order.txt"
    ordered = [line.strip() for line in order_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    missing = [name for name in ordered if not (REPORT / name).is_file()]
    available = [REPORT / name for name in ordered if (REPORT / name).is_file()]
    if not available:
        raise SystemExit("No report Markdown files from order.txt are present.")

    DIST.mkdir(parents=True, exist_ok=True)
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(35, 42, 54)
    for style_name, size, color in (
        ("Heading 1", 18, RGBColor(24, 62, 112)),
        ("Heading 2", 14, RGBColor(30, 94, 150)),
        ("Heading 3", 12, RGBColor(42, 105, 156)),
    ):
        style = document.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.color.rgb = color

    if missing:
        document.add_heading("Trạng thái bản ghép — bản nháp chưa đầy đủ", level=1)
        document.add_paragraph(
            f"Có {len(missing)} trong {len(ordered)} tệp theo thứ tự báo cáo chưa tồn tại tại thời điểm dựng. "
            "Bản DOCX này chỉ ghép các tệp hiện có; không thay thế bản nộp cuối kỳ."
        )
        for name in missing:
            document.add_paragraph(name, style="List Bullet")
        document.add_page_break()

    for section_index, source in enumerate(available):
        if section_index:
            document.add_page_break()
        add_markdown(document, source)

    document.core_properties.title = "Connect Four AI — Báo cáo cuối kỳ Nhóm 26 (bản ghép làm việc)"
    document.core_properties.author = "Nhóm 26"
    document.core_properties.subject = "Generated from available Markdown sections in docs/report/order.txt"
    document.save(OUTPUT)
    print(f"Built: {OUTPUT}")
    print(f"Included: {len(available)}/{len(ordered)} ordered Markdown files")
    if missing:
        print("Missing sections: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
