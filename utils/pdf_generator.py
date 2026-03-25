from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os
from datetime import datetime
import html

def generate_pdf_report(record):

    patient_id = str(record.get("Patient ID", "UnknownID")).strip()
    patient_name = str(record.get("Patient Name", "UnknownName")).strip()
    test_mode = str(record.get("Test Mode", "UnknownTest")).strip()

    def sanitize(value):
        return "".join(c for c in value if c.isalnum() or c in ("_", "-"))

    safe_id = sanitize(patient_id)
    safe_name = sanitize(patient_name.replace(" ", "_"))
    safe_test = sanitize(test_mode.replace(" ", "_"))

    filename = f"{safe_id}_{safe_name}_{safe_test}.pdf"

    reports_dir = os.path.join(os.getcwd(), "reports")

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    filepath = os.path.join(reports_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = styles["Heading2"]

    elements.append(Paragraph("<b>Dyslexia Screening Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- PATIENT INFO ----------------
    elements.append(Paragraph(f"<b>Patient ID:</b> {html.escape(record.get('Patient ID',''))}", normal))
    elements.append(Paragraph(f"<b>Patient Name:</b> {html.escape(record.get('Patient Name',''))}", normal))
    elements.append(Paragraph(f"<b>Date:</b> {html.escape(record.get('Timestamp',''))}", normal))
    elements.append(Paragraph(f"<b>Test Mode:</b> {html.escape(record.get('Test Mode',''))}", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- CHARACTER ----------------
    elements.append(Paragraph("<b>Character Test</b>", heading))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Given:</b> {html.escape(record.get('Character Given',''))}", normal))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Response:</b> {html.escape(record.get('Character Response',''))}", normal))
    elements.append(Paragraph(f"<b>Score:</b> {record.get('Character Score','')}", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- WORD ----------------
    elements.append(Paragraph("<b>Word Test</b>", heading))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Given:</b> {html.escape(record.get('Word Given',''))}", normal))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Response:</b> {html.escape(record.get('Word Response',''))}", normal))
    elements.append(Paragraph(f"<b>Score:</b> {record.get('Word Score','')}", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- SENTENCE ----------------
    elements.append(Paragraph("<b>Sentence Test</b>", heading))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Given:</b> {html.escape(record.get('Sentence Given',''))}", normal))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Response:</b> {html.escape(record.get('Sentence Response',''))}", normal))
    elements.append(Paragraph(f"<b>Score:</b> {record.get('Sentence Score','')}", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- IMAGE ----------------
    elements.append(Paragraph("<b>Image Text Test</b>", heading))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Given:</b> {html.escape(record.get('Image Text Given',''))}", normal))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Response:</b> {html.escape(record.get('Image Response',''))}", normal))
    elements.append(Paragraph(f"<b>Score:</b> {record.get('Image Score','')}", normal))
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- FINAL ----------------
    elements.append(Paragraph("<b>Final Result</b>", heading))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Final Score:</b> {record.get('Final Score','')}%", normal))
    elements.append(Paragraph(f"<b>Risk Level:</b> {html.escape(record.get('Risk Level',''))}", normal))

    if record.get("Audio Confidence (%)"):
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(
            f"<b>Audio Confidence:</b> {record.get('Audio Confidence (%)')}%",
            normal
        ))

    doc.build(elements)

    return filepath