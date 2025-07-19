import json
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_report_json(results):
    """Return results as pretty-printed JSON bytes for download."""
    return json.dumps(results, indent=2).encode("utf-8")

def generate_report_pdf(results):
    """
    Generate a PDF summary report for test results.
    Returns bytes for Streamlit download_button.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 30
    y = height - margin

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "AI Test Suite v2 - PDF Report")
    y -= 25

    # Date
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20

    # Table header
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Scenario")
    c.drawString(margin + 180, y, "Plugin")
    c.drawString(margin + 320, y, "Status")
    c.drawString(margin + 400, y, "Notes")
    y -= 18
    c.setFont("Helvetica", 10)
    c.line(margin, y, width - margin, y)
    y -= 14

    # Rows
    for entry in results:
        scenario = entry.get("scenario", "N/A")
        plugin = entry.get("plugin", "N/A")
        res = entry.get("result", {})
        if isinstance(res, dict):
            status = res.get("risk_level", res.get("status", res.get("result", "N/A")))
            notes = res.get("recommendation", res.get("error", res.get("details", "")))
            if isinstance(notes, list): notes = "; ".join(notes)
        else:
            status = str(res)
            notes = ""
        # Fit to line
        scenario = (scenario[:26] + '...') if len(str(scenario)) > 29 else str(scenario)
        plugin = (plugin[:14] + '...') if len(str(plugin)) > 17 else str(plugin)
        status = str(status)
        notes = str(notes)
        c.drawString(margin, y, scenario)
        c.drawString(margin + 180, y, plugin)
        c.drawString(margin + 320, y, status)
        c.drawString(margin + 400, y, notes[:45])
        y -= 16
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - margin

    # Legend & footer
    if y < 120:
        c.showPage()
        y = height
