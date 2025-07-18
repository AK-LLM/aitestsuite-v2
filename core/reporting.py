"""
Multi-format reporting: HTML, TXT, PDF (with ReportLab), CSV.
"""
import json

def save_html(report_data, path):
    html = f"<html><body><h2>AI Test Report</h2><pre>{json.dumps(report_data, indent=2)}</pre></body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def save_txt(report_data, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(report_data, indent=2))

def save_csv(results, path):
    import csv
    # Assume results is a list of dicts
    if not results:
        return
    keys = results[0].keys()
    with open(path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)

def save_pdf(report_data, path):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(path, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 10)
    lines = json.dumps(report_data, indent=2).splitlines()
    for line in lines:
        text.textLine(line)
    c.drawText(text)
    c.save()
