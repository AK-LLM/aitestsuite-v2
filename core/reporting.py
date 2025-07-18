"""
Reporting utilities: HTML, PDF, CSV, JSON.
"""

def save_html(report_data, path):
    html = f"<html><body><h2>AI Test Report</h2><pre>{report_data}</pre></body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def save_txt(report_data, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(report_data))

