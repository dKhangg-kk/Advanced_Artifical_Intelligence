#!/usr/bin/env python3
"""Ghep bao cao Markdown thanh Word (.docx) va PDF bang pandoc + LibreOffice.

Khac ``build_report.py`` (ban ghep nhanh bang python-docx, khong co hinh, cong thuc
va muc luc), script nay:

* dung pandoc nen giu duoc hinh trong ``results/figures``, bang, cong thuc LaTeX
  (chuyen thanh cong thuc Word) va chu thich hinh;
* tao trang bia tu ``00_bia_muc_luc.md`` va muc luc tu dong (truong TOC cua Word);
* gom cac tep thanh 5 chuong theo ``order.txt``: chen tieu de "Chuong N" va ha
  mot cap tieu de cua cac tep con trong Chuong 2-4;
* dinh dang theo thong le bao cao: A4, Times New Roman 13, le trai 3 cm, phai 2 cm,
  tren/duoi 2 cm, gian dong 1,3, so trang o chan trang;
* xuat PDF bang LibreOffice (cap nhat muc luc truoc khi xuat).

Chay tu ``Connect_Four/``:

    python docs/report/build_docx_pdf.py                 # ca bao cao
    python docs/report/build_docx_pdf.py --part nhu-y    # chi cac muc cua Nhu Y
    python docs/report/build_docx_pdf.py --no-pdf        # chi .docx

Yeu cau: pandoc >= 2.19, python-docx; LibreOffice (``soffice``) de xuat PDF.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "report"
DIST = REPORT / "dist"
GROUP = "Nhom26"

# Tep dau tien cua moi chuong (theo order.txt) -> tieu de chuong chen truoc no.
CHAPTER_START = {
    "01_gioi_thieu.md": "Chương 1. Giới thiệu",
    "02a_tim_kiem.md": "Chương 2. Cơ sở lý thuyết",
    "03a_kien_truc.md": "Chương 3. Thiết kế và cài đặt",
    "04a_ket_qua.md": "Chương 4. Thực nghiệm và thảo luận",
}
# Tep tu mang tieu de cap 1 cua minh (khong ha cap).
STANDALONE = {"05_ket_luan.md", "06_tai_lieu_dong_gop.md"}

PARTS = {
    "nhu-y": {
        "files": [
            "02c_hoc_tang_cuong.md",
            "03d_dqn_giai_dau.md",
            "04a_ket_qua.md",
            "04c_dqn_duong_cong.md",
            "04f_ablation_dqn.md",
            "04h_thao_luan.md",
        ],
        "title": "PHẦN VIỆC CỦA PHAN LÊ NGỌC NHƯ Ý (3124720079)",
        "subtitle": "Cấp 6 (DQN), giải đấu Round-Robin, kết quả và thảo luận — mục 2.4, 3.5–3.6, 4.1–4.5 (DQN), 4.7",
        "output": f"BaoCao_{GROUP}_PhanNhuY_DQN_GiaiDau",
    }
}

PAGE_BREAK = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'


# --------------------------------------------------------------------------- Markdown
def _strip_relative_links(text: str) -> str:
    """Link toi tep trong repo (khong phai http) khong mo duoc trong Word -> giu chu, bo dich."""

    def repl(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        return label

    # Khong dung vao anh: (?<!!)
    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)", repl, text)


def _shift_headings(text: str, by: int) -> str:
    out = []
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#{1,5}\s", line):
            line = "#" * by + line
        out.append(line)
    return "\n".join(out)


def _section_text(name: str, shift: int) -> str:
    text = (REPORT / name).read_text(encoding="utf-8-sig")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = _strip_relative_links(text)
    if name == "01_gioi_thieu.md":
        text = re.sub(r"^# .*$", "", text, count=1, flags=re.M)  # thay bang "Chuong 1"
    elif shift:
        text = _shift_headings(text, shift)
    return text.strip() + "\n"


def _cover(title: str | None = None, subtitle: str | None = None) -> str:
    """Trang bia lay tu 00_bia_muc_luc.md (phan truoc '## Muc luc')."""
    raw = (REPORT / "00_bia_muc_luc.md").read_text(encoding="utf-8-sig")
    raw = raw.split("## Mục lục")[0]
    raw = re.sub(r"^>.*$", "", raw, flags=re.M)
    lines = [ln.rstrip() for ln in raw.splitlines()]
    blocks: list[str] = []

    def div(style: str, content: str) -> str:
        return f'::: {{custom-style="{style}"}}\n{content}\n:::\n'

    members: list[str] = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not re.fullmatch(r"[-: ]+", "".join(cells)) and not cells[0].startswith("Họ"):
                members.append(f"{cells[0]} — {cells[1]}")
            continue
        if members:
            blocks.append(div("Cover Text", "\\\n".join(members)))
            blocks.append(div("Cover Spacer", "&nbsp;"))
            members = []
        if not s or (s.startswith("*") and s.endswith("*") and not s.startswith("**")):
            continue
        s = s.rstrip("\\ ").rstrip()
        if s.startswith("# "):
            blocks.append(div("Cover Spacer", "&nbsp;"))
            blocks.append(div("Cover Title", title or s[2:]))
            if subtitle:
                blocks.append(div("Cover Subtitle", subtitle))
            blocks.append(div("Cover Spacer", "&nbsp;"))
        elif s.startswith("## "):
            if not subtitle:
                blocks.append(div("Cover Subtitle", s[3:]))
                blocks.append(div("Cover Spacer", "&nbsp;"))
        elif s.startswith("**Trường:**"):
            blocks.insert(0, div("Cover Header", "TRƯỜNG " + s.split("**", 2)[2].strip().upper()))
        else:
            blocks.append(div("Cover Text", s))
    if members:
        blocks.append(div("Cover Text", "\\\n".join(members)))
    blocks.append(div("Cover Spacer", "&nbsp;"))
    blocks.append(div("Cover Text", "TP. Hồ Chí Minh, tháng 11 năm 2026"))
    return "\n".join(blocks)


def assemble(files: list[str], part: dict | None) -> str:
    chunks = [_cover(part["title"], part["subtitle"]) if part else _cover()]
    chunks.append('```{=openxml}\n<w:p><w:pPr><w:pStyle w:val="TOCHeading"/></w:pPr>'
                  '<w:r><w:t>MỤC LỤC</w:t></w:r></w:p>\n```\n')
    chunks.append("```{=openxml}\n" + _toc_field() + "\n```\n")
    first = True
    for name in files:
        chunks.append(PAGE_BREAK)
        if part:
            chunks.append(_section_text(name, shift=0))
            continue
        if name in CHAPTER_START:
            chunks.append(f"# {CHAPTER_START[name]}\n")
        shift = 0 if name in STANDALONE else 1
        chunks.append(_section_text(name, shift=shift))
        first = False
    return "\n".join(chunks)


def _toc_field() -> str:
    return (
        '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:t>Nhấn chuột phải → Update Field để cập nhật mục lục.</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


# --------------------------------------------------------------------------- reference.docx
def _set_font(style, name: str, size: float | None = None, bold: bool | None = None,
              color: RGBColor | None = None) -> None:
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), name)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if fonts.get(qn(attr)) is not None:
            del fonts.attrib[qn(attr)]
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color is not None:
        style.font.color.rgb = color


def _page_number_footer(section) -> None:
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, " PAGE "), ("separate", None), (None, "1"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        elif text.strip() == "PAGE":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        else:
            el = OxmlElement("w:t")
            el.text = text
        run._r.append(el)


def make_reference_docx(path: Path) -> None:
    subprocess.run(["pandoc", "-o", str(path), "--print-default-data-file", "reference.docx"],
                   check=True, capture_output=True)
    doc = Document(str(path))
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.left_margin, section.right_margin = Cm(3.0), Cm(2.0)
    section.top_margin, section.bottom_margin = Cm(2.0), Cm(2.0)
    _page_number_footer(section)

    navy = RGBColor(0x1F, 0x3A, 0x68)
    raw_styles = doc.styles

    class _Styles:
        """Tra style theo ten hien thi (python-docx doi 'Heading 1' -> 'heading 1' khi tra cuu)."""

        def __getitem__(self, name):
            for style in raw_styles:
                if style.name == name:
                    return style
            raise KeyError(name)

        def __iter__(self):
            return iter(raw_styles)

        def add_style(self, *args):
            return raw_styles.add_style(*args)

    styles = _Styles()
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        if name in [s.name for s in styles]:
            st = styles[name]
            _set_font(st, "Times New Roman", 13)
            st.paragraph_format.line_spacing = 1.3
            st.paragraph_format.space_after = Pt(4)
            if name != "Compact":
                st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 13), ("Heading 4", 13)):
        st = styles[name]
        _set_font(st, "Times New Roman", size, bold=True, color=navy)
        st.paragraph_format.space_before = Pt(12 if name != "Heading 1" else 0)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True
        if name == "Heading 4":
            st.font.italic = True
    styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for name in ("Title", "Subtitle", "Author", "Date", "Abstract", "Block Text", "Caption",
                 "Image Caption", "Table Caption", "Bibliography", "Hyperlink", "TOC Heading"):
        if name in [s.name for s in styles]:
            st = styles[name]
            if st.type == 1:  # paragraph
                _set_font(st, "Times New Roman")
    for name in ("Image Caption", "Table Caption", "Caption"):
        if name in [s.name for s in styles]:
            st = styles[name]
            _set_font(st, "Times New Roman", 11.5)
            st.font.italic = True
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if "Block Text" in [s.name for s in styles]:
        st = styles["Block Text"]
        _set_font(st, "Times New Roman", 12)
        st.font.italic = True
    if "Source Code" in [s.name for s in styles]:
        _set_font(styles["Source Code"], "Consolas", 9.5)
    if "Verbatim Char" in [s.name for s in styles]:
        _set_font(styles["Verbatim Char"], "Consolas", 11)
    if "TOC Heading" in [s.name for s in styles]:
        st = styles["TOC Heading"]
        _set_font(st, "Times New Roman", 16, bold=True, color=navy)
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        st.paragraph_format.page_break_before = True  # muc luc luon bat dau trang moi sau bia
    from docx.enum.style import WD_STYLE_TYPE

    for name, size, bold, space in (("Cover Title", 20, True, 18), ("Cover Subtitle", 15, True, 12),
                                    ("Cover Text", 13, False, 4), ("Cover Header", 14, True, 6),
                                    ("Cover Spacer", 13, False, 40)):
        st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles["Normal"]
        _set_font(st, "Times New Roman", size, bold=bold, color=navy if bold else None)
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        st.paragraph_format.space_after = Pt(space)
    # TOC 1-3: Times New Roman
    for level in (1, 2, 3):
        name = f"toc {level}"
        try:
            st = styles[name]
        except KeyError:
            st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = styles["Normal"]
        _set_font(st, "Times New Roman", 12.5, bold=(level == 1))
        st.paragraph_format.left_indent = Cm(0.6 * (level - 1))
        st.paragraph_format.space_after = Pt(1)
    doc.save(str(path))


# --------------------------------------------------------------------------- post-processing
def _style_tables(docx_path: Path) -> None:
    """Ke vien bang, chu 10,5 pt, hang tieu de dam va lap lai khi sang trang."""
    doc = Document(str(docx_path))
    for table in doc.tables:
        tbl_pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "8C99A6")
            borders.append(el)
        existing = tbl_pr.find(qn("w:tblBorders"))
        if existing is not None:
            tbl_pr.remove(existing)
        tbl_pr.append(borders)
        width = OxmlElement("w:tblW")
        width.set(qn("w:w"), "5000")
        width.set(qn("w:type"), "pct")
        old = tbl_pr.find(qn("w:tblW"))
        if old is not None:
            tbl_pr.remove(old)
        tbl_pr.append(width)
        for r_index, row in enumerate(table.rows):
            if r_index == 0:
                tr_pr = row._tr.get_or_add_trPr()
                header = OxmlElement("w:tblHeader")
                tr_pr.append(header)
            for cell in row.cells:
                if r_index == 0:
                    shading = OxmlElement("w:shd")
                    shading.set(qn("w:val"), "clear")
                    shading.set(qn("w:fill"), "E3EAF3")
                    cell._tc.get_or_add_tcPr().append(shading)
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = 1.0
                    paragraph.paragraph_format.space_after = Pt(1)
                    paragraph.paragraph_format.alignment = None
                    for run in paragraph.runs:
                        run.font.size = Pt(10.5)
                        if r_index == 0:
                            run.font.bold = True
    doc.save(str(docx_path))


def _build_pdf(docx_path: Path) -> Path:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise SystemExit("Khong tim thay LibreOffice (soffice) de xuat PDF; dung --no-pdf.")
    script = Path(tempfile.gettempdir()) / "c4_update_toc_export.py"
    script.write_text(_UNO_SCRIPT, encoding="utf-8")
    profile = Path(tempfile.mkdtemp(prefix="lo_profile_"))
    out_pdf = docx_path.with_suffix(".pdf")
    python_uno = _libreoffice_python(soffice)
    proc = subprocess.Popen(
        [soffice, f"-env:UserInstallation=file://{profile}", "--headless", "--invisible", "--norestore",
         "--accept=socket,host=127.0.0.1,port=2083;urp;"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        subprocess.run([python_uno, str(script), str(docx_path), str(out_pdf)], check=True, timeout=600)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    return out_pdf


def _libreoffice_python(soffice: str) -> str:
    for candidate in ("/usr/bin/python3", sys.executable):
        try:
            subprocess.run([candidate, "-c", "import uno"], check=True, capture_output=True)
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    program_dir = Path(soffice).resolve().parent
    bundled = program_dir / "python"
    if bundled.exists():
        return str(bundled)
    raise SystemExit("Khong tim thay Python co module 'uno' cua LibreOffice.")


_UNO_SCRIPT = r'''
import sys, time, uno
from com.sun.star.beans import PropertyValue

def prop(name, value):
    p = PropertyValue(); p.Name = name; p.Value = value; return p

src, dst = sys.argv[1], sys.argv[2]
local = uno.getComponentContext()
resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
for _ in range(60):
    try:
        ctx = resolver.resolve("uno:socket,host=127.0.0.1,port=2083;urp;StarOffice.ComponentContext")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Khong ket noi duoc LibreOffice")
desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (prop("Hidden", True),))
doc.refresh()
indexes = doc.getDocumentIndexes()
for i in range(indexes.getCount()):
    indexes.getByIndex(i).update()
doc.refresh()
for i in range(indexes.getCount()):
    indexes.getByIndex(i).update()
doc.storeToURL(uno.systemPathToFileUrl(dst), (prop("FilterName", "writer_pdf_Export"),))
doc.close(True)
'''


# --------------------------------------------------------------------------- main
def build(files: list[str], output_stem: str, part: dict | None, pdf: bool) -> list[Path]:
    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        reference = tmp_dir / "reference.docx"
        make_reference_docx(reference)
        markdown = tmp_dir / "report.md"
        markdown.write_text(assemble(files, part), encoding="utf-8")
        out_docx = DIST / f"{output_stem}.docx"
        title = part["title"] if part else "Connect Four AI — Báo cáo đồ án cuối kỳ Nhóm 26"
        subprocess.run(
            ["pandoc", str(markdown), "-f", "markdown+pipe_tables+tex_math_dollars+implicit_figures",
             "-t", "docx", "--reference-doc", str(reference), "--resource-path", str(REPORT),
             "--metadata", f"title-meta={title}", "--metadata", "author-meta=Nhóm 26",
             "-o", str(out_docx)],
            check=True, cwd=REPORT,
        )
    _style_tables(out_docx)
    outputs = [out_docx]
    if pdf:
        outputs.append(_build_pdf(out_docx))
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ghep bao cao thanh .docx va PDF (pandoc + LibreOffice)")
    parser.add_argument("--part", choices=sorted(PARTS), help="chi xuat cac muc cua mot thanh vien")
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args(argv)
    if shutil.which("pandoc") is None:
        raise SystemExit("Can pandoc; neu khong co, dung docs/report/build_report.py (ban nhanh, khong co hinh).")
    if args.part:
        part = PARTS[args.part]
        files, stem = part["files"], part["output"]
    else:
        part = None
        ordered = [ln.strip() for ln in (REPORT / "order.txt").read_text(encoding="utf-8-sig").splitlines()
                   if ln.strip()]
        files = [name for name in ordered if name != "00_bia_muc_luc.md"]
        missing = [name for name in files if not (REPORT / name).is_file()]
        if missing:
            raise SystemExit(f"Thieu tep theo order.txt: {missing}")
        stem = f"BaoCao_CuoiKy_{GROUP}"
    for path in build(files, stem, part, pdf=not args.no_pdf):
        print(f"Built: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
