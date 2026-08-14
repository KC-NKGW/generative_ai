from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from images import UPLOAD_DIR

FONT_NAME = "HeiseiMin-W3"
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))

IMAGE_COL_WIDTH = 45 * mm
TEXT_COL_WIDTH = 130 * mm
MAX_IMAGE_SIDE = 45 * mm


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("JTitle", parent=base["Title"], fontName=FONT_NAME, fontSize=18),
        "heading": ParagraphStyle("JHeading", parent=base["Heading2"], fontName=FONT_NAME, fontSize=13),
        "body": ParagraphStyle("JBody", parent=base["Normal"], fontName=FONT_NAME, fontSize=10, leading=14),
        "meta": ParagraphStyle(
            "JMeta", parent=base["Normal"], fontName=FONT_NAME, fontSize=9, leading=13,
            textColor=colors.HexColor("#4B5160"),
        ),
        "noimg": ParagraphStyle("JNoImg", fontName=FONT_NAME, fontSize=9, textColor=colors.grey),
    }


def _image_flowable(filename, styles):
    path = UPLOAD_DIR / filename if filename else None
    if not path or not path.exists():
        return Paragraph("(写真なし)", styles["noimg"])

    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    width = MAX_IMAGE_SIDE
    height = width * ratio
    if height > MAX_IMAGE_SIDE:
        height = MAX_IMAGE_SIDE
        width = height / ratio
    img.drawWidth = width
    img.drawHeight = height
    return img


def _entry_flowables(entry, styles):
    kind = "外食" if entry["is_eating_out"] else "内食"
    lines = [f"{entry['eaten_date']}　{kind}"]
    if entry["restaurant_name"]:
        lines.append(f"店名: {entry['restaurant_name']}")
    if entry["location"]:
        lines.append(f"場所: {entry['location']}")
    if entry["reference_url"]:
        lines.append(f'<link href="{entry["reference_url"]}">{entry["reference_url"]}</link>')

    text_flowables = [Paragraph(entry["dish_name"], styles["heading"])]
    for line in lines:
        text_flowables.append(Paragraph(line, styles["meta"]))
    if entry["comment"]:
        text_flowables.append(Spacer(1, 2 * mm))
        text_flowables.append(Paragraph(entry["comment"].replace("\n", "<br/>"), styles["body"]))

    table = Table(
        [[_image_flowable(entry["screenshot_filename"], styles), text_flowables]],
        colWidths=[IMAGE_COL_WIDTH, TEXT_COL_WIDTH],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    return KeepTogether([
        table,
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", color=colors.HexColor("#D8D2C2"), thickness=0.5),
        Spacer(1, 5 * mm),
    ])


def build_pdf(entries):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
    )
    styles = _styles()

    story = [
        Paragraph("お墓飯 記録一覧", styles["title"]),
        Paragraph(f"書き出し日: {date.today().isoformat()}　全{len(entries)}件", styles["meta"]),
        Spacer(1, 10 * mm),
    ]
    for entry in entries:
        story.append(_entry_flowables(entry, styles))

    doc.build(story)
    buffer.seek(0)
    return buffer
