"""
Advanced reporting with legend, risk mapping, charts, and industry cross-references.
"""

import json
from collections import Counter

RISK_LEVELS = {
    "Critical": "#ff2d00",
    "High": "#ff9900",
    "Medium": "#ffd000",
    "Low": "#66bb6a",
    "Pass": "#4caf50",
    "Unknown": "#cccccc"
}

INDUSTRY_REFERENCES = {
    "LLM01": "Prompt Injection (OWASP LLM Top 10)",
    "LLM02": "Training Data Leakage (OWASP LLM Top 10)",
    "Bias": "NIST AI RMF 2.1",
    "Jailbreak": "Anthropic Red Team Playbook",
    "Robustness": "OpenAI Evals"
}

def generate_legend_html():
    return "<h3>Risk Legend</h3>" + "".join(
        f"<div style='background:{color};padding:5px;'>{risk}: {desc}</div>"
        for risk, color in RISK_LEVELS.items()
        for desc in [risk]
    )

def generate_report(results):
    # Pie/bar charts: risk levels, plugin hits
    risk_counts = Counter([r.get("risk","Unknown") for r in results])
    html = "<html><head><title>AI Security Report</title></head><body>"
    html += "<h1>AI Test Suite Report</h1>"
    html += "<h2>Summary</h2>"
    html += "<ul>"
    for risk, count in risk_counts.items():
        html += f"<li style='color:{RISK_LEVELS.get(risk, '#ccc')}'>{risk}: {count}</li>"
    html += "</ul>"
    html += generate_legend_html()
    html += "<h2>Findings</h2><table border=1 cellpadding=5>"
    html += "<tr><th>Test</th><th>Plugin</th><th>Risk</th><th>References</th><th>Result/Details</th></tr>"
    for r in results:
        refs = [INDUSTRY_REFERENCES.get(ref, ref) for ref in r.get("references",[])]
        html += (
            "<tr>"
            f"<td>{r['scenario'].get('name','')}</td>"
            f"<td>{r.get('plugin','')}</td>"
            f"<td style='color:{RISK_LEVELS.get(r.get('risk','Unknown'),'#ccc')}'>{r.get('risk','')}</td>"
            f"<td>{', '.join(refs)}</td>"
            f"<td>{json.dumps(r.get('result',r.get('error','')),indent=2)}</td>"
            "</tr>"
        )
    html += "</table>"
    html += "<h2>Glossary & Fixes</h2><ul>"
    html += "<li><b>Critical:</b> Immediate action. Example: Model responds to injected prompt (LLM01, OWASP).</li>"
    html += "<li><b>High:</b> High business/security risk; fix soon. Example: Data exfiltration prompt not blocked.</li>"
    html += "<li><b>Medium:</b> Advisory. Example: Weakness in context retention, but no active leak found.</li>"
    html += "<li><b>Low:</b> Minor or unlikely issue.</li>"
    html += "<li><b>Pass:</b> No risk detected.</li>"
    html += "</ul></body></html>"
    return html

def save_html(report_html, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_html)

def save_pdf(report_html, path):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    import html2text
    text = html2text.html2text(report_html)
    c = canvas.Canvas(path, pagesize=letter)
    for i, line in enumerate(text.splitlines()):
        c.drawString(40, 750 - 12 * i, line)
        if 750 - 12 * i < 50:
            c.showPage()
    c.save()

def save_csv(results, path):
    import csv
    keys = ["test", "plugin", "risk", "references", "result"]
    with open(path, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(keys)
        for r in results:
            writer.writerow([
                r['scenario'].get('name',''),
                r.get('plugin',''),
                r.get('risk',''),
                ", ".join(r.get('references',[])),
                json.dumps(r.get('result',r.get('error','')))
            ])
