#!/home/hermes/.venv/bin/python3
"""Generate a PDF summary from /tmp/papers.json. Output: /tmp/ai-papers-summary.pdf"""
import json, sys
from pathlib import Path

INPUT = "/tmp/papers.json"
OUTPUT = "/tmp/ai-papers-summary.pdf"

try:
    from reportlab.lib.pagesizes import letter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "-q"])
    from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

papers = json.loads(Path(INPUT).read_text())
doc = SimpleDocTemplate(OUTPUT, pagesize=letter,
                        rightMargin=inch, leftMargin=inch,
                        topMargin=inch, bottomMargin=inch)
styles = getSampleStyleSheet()
title_style = ParagraphStyle("PaperTitle", parent=styles["Heading2"], spaceAfter=6)
body_style = styles["BodyText"]
body_style.spaceAfter = 4

story = []
story.append(Paragraph("Top AI Papers — Summary", styles["Title"]))
story.append(Spacer(1, 0.3 * inch))
for i, p in enumerate(papers, 1):
    story.append(Paragraph(f"{i}. {p['title']}", title_style))
    if p.get("authors"):
        story.append(Paragraph(f"<i>{p['authors']}</i>", body_style))
    story.append(Paragraph(p["summary"].replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 0.2 * inch))
doc.build(story)
print(f"PDF written to {OUTPUT} ({len(papers)} papers)")
