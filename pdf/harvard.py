import re
import unicodedata
from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
FONT_NAME = "DejaVu"

CHAR_REPLACEMENTS = {
    "č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "d",
    "Č": "C", "Ć": "C", "Ž": "Z", "Š": "S", "Đ": "D",
    "ł": "l", "ą": "a", "ę": "e", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    "Ł": "L", "Ą": "A", "Ę": "E", "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z",
    "\u2013": "-", "\u2014": "-",
    "\u201c": '"', "\u201d": '"',
    "\u2018": "'", "\u2019": "'",
    "\u2022": "-", "•": "-",
}

URL_PATTERN = re.compile(
    r"((?:https?://)?(?:www\.)?(?:github\.com|linkedin\.com)[^\s|]*)",
    re.IGNORECASE,
)
PIPE_SEPARATOR = " | "
CONTENT_WIDTH = 180
CONTROL_CHARS_PATTERN = re.compile(r"[\u200b\u200c\u200d\ufeff]")
SPACE_CHARS_PATTERN = re.compile(r"[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]")
PLUS_CHARS_PATTERN = re.compile(r"[\uff0b\ufe62]")


class HarvardPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass


def _resolve_font_family(pdf: HarvardPDF) -> str:
    regular = FONT_DIR / "DejaVuSerif.ttf"
    bold = FONT_DIR / "DejaVuSerif-Bold.ttf"
    if regular.exists() and bold.exists():
        pdf.add_font(FONT_NAME, "", str(regular))
        pdf.add_font(FONT_NAME, "B", str(bold))
        return FONT_NAME
    return "Times"


def sanitize_text(text: str, force_latin1: bool = False) -> str:
    text = unicodedata.normalize("NFKC", str(text))
    text = SPACE_CHARS_PATTERN.sub(" ", text)
    text = CONTROL_CHARS_PATTERN.sub("", text)
    text = PLUS_CHARS_PATTERN.sub("+", text)
    for char, replacement in CHAR_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    text = "".join("\ufffd" if unicodedata.category(char) == "Cs" else char for char in text)
    if force_latin1:
        text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def strip_inline_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


def draw_section_line(pdf, y=None):
    if y is None:
        y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    pdf.line(15, y, 195, y)


def split_pipe_line(line: str) -> list[str]:
    fields = [field.strip() for field in line.split("|") if field.strip()]
    if len(fields) >= 4:
        return [PIPE_SEPARATOR.join(fields[:2]), PIPE_SEPARATOR.join(fields[2:])]
    return [PIPE_SEPARATOR.join(fields)] if fields else [line]


def render_url_line(pdf, line, line_height):
    line = sanitize_text(line)
    segments = URL_PATTERN.split(line)
    if "|" in line:
        total_w = sum(pdf.get_string_width(seg) for seg in segments if seg)
        start_x = max(15, 15 + (CONTENT_WIDTH - total_w) / 2)
        pdf.set_x(start_x)
    for seg in segments:
        if not seg:
            continue
        if URL_PATTERN.fullmatch(seg):
            url = seg if seg.startswith("http") else f"https://{seg}"
            pdf.set_text_color(17, 85, 204)
            pdf.cell(pdf.get_string_width(seg), line_height, seg, link=url)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.cell(pdf.get_string_width(seg), line_height, seg)
    pdf.ln(line_height)


def render_pipe_line(pdf, line, line_height):
    for contact_line in split_pipe_line(line):
        if URL_PATTERN.search(contact_line):
            render_url_line(pdf, contact_line, line_height)
        else:
            pdf.cell(CONTENT_WIDTH, line_height, contact_line, align="C")
            pdf.ln(line_height)


def convert_markdown_to_harvard_pdf(md_text: str) -> bytes:
    pdf = HarvardPDF()
    font = _resolve_font_family(pdf)
    md_text = sanitize_text(md_text, force_latin1=(font == "Times"))
    pdf.add_page()
    pdf.set_margins(15, 12, 15)
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font(font, size=10)

    header_block_ended = False
    for line in md_text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(1.2)
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)

        if line.startswith("# "):
            name = strip_inline_md(line[2:])
            pdf.set_font(font, "B", size=16)
            pdf.cell(CONTENT_WIDTH, 7, name, align="C")
            pdf.ln(7)
            header_block_ended = False
        elif line.startswith("## "):
            if not header_block_ended:
                pdf.ln(1)
                draw_section_line(pdf)
                pdf.ln(2)
                header_block_ended = True
            section = strip_inline_md(line[3:]).upper()
            pdf.ln(2)
            pdf.set_font(font, "B", size=10)
            pdf.cell(CONTENT_WIDTH, 4, section)
            pdf.ln(5)
            draw_section_line(pdf)
            pdf.ln(2)
        elif line.startswith("### "):
            sub = strip_inline_md(line[4:])
            pdf.set_font(font, "B", size=9)
            pdf.cell(CONTENT_WIDTH, 4, sub)
            pdf.ln(4.5)
            header_block_ended = True
        elif line.startswith(("* ", "- ")):
            bullet_text = strip_inline_md(line[2:])
            pdf.set_font(font, size=9)
            pdf.set_x(20)
            pdf.cell(4, 3.8, "-", ln=False)
            pdf.multi_cell(171, 3.8, bullet_text)
            pdf.set_x(15)
            header_block_ended = True
        else:
            clean = strip_inline_md(line)
            pdf.set_font(font, size=9)
            if "|" in clean:
                render_pipe_line(pdf, clean, 3.5)
            elif URL_PATTERN.search(clean):
                render_url_line(pdf, clean, 3.5)
            else:
                pdf.multi_cell(CONTENT_WIDTH, 3.8, clean)
                pdf.set_x(15)

    return bytes(pdf.output())
