import json
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import base64
import io

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

FIX_GUIDES = {
    "Critical": "Block all prompt injections, improve input validation, add role/context hardening, and patch model API configuration.",
    "High": "Patch LLM config, use external filter, monitor logs for suspicious requests, restrict system prompt exposure.",
    "Medium": "Review persona handling, tune model memory, add audit of context switching.",
    "Low": "Monitor for low-severity issues, continue regular updates.",
    "Pass": "No action needed.",
    "Unknown": "Review new risks as industry knowledge evolves."
}

def make_risk_pie(risk_counts):
    labels, sizes, colors = [], [], []
    for risk, count in risk_counts.items():
        labels.append(risk)
        sizes.append(count)
        colors.append(RISK_LEVELS.get(risk, "#ccc"))
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"<img src='data:image/png;base64,{encoded}'/>"

def make_heatmap(results):
    # Heatmap: rows=plugins, cols=risk levels
    import numpy as np
    import seaborn as sns
    plugin_names = list({r.get("plugin", "Unknown") for r in results})
    risks = list(RISK_LEVELS.keys())
    matrix = np.zeros((len(plugin_names), len(risks)), dtype=int)
    for i, plugin in enumerate(plugin_names):
        for j, risk in enumerate(risks):
            matrix[i, j] = sum(1 for r in results if r.get("plugin", "Unknown") == plugin and r.get("risk") == risk)
    fig, ax = plt.subplots(figsize=(8, max(2, len(plugin_names)//2)))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="YlOrRd", xticklabels=risks, yticklabels=plugin_names, cbar=False, linewidths=0.5, linecolor='grey')
    ax.set_title("Risk Heatmap by Plugin")
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"<img src='data:image/png;base64,{encoded}'/>"

def generate_legend_html():
    return "<h3>Risk Legend</h3>" + "".join(
        f"<div style='background:{color};padding:5px;margin-bottom:2px'>{risk}: {desc}</div>"
        for risk, color in RISK_LEVELS.items()
        for desc in [risk]
    )

def generate_report(results):
    # Pie/bar charts: risk levels, plugin hits
    risk_counts = Counter([r.get("risk","Unknown") for r in results])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = "<html><head><title>AI Security Report</title></head><body style='font-family:sans-serif'>"
    html += f"<h1>AI Test Suite Risk Report</h1><h3>Date: {now}</h3>"
    html += "<h2>Summary</h2>"
    html += make_risk_pie(risk_counts)
    html += make_heatmap(results)
    html += "<ul>"
    for risk, count in risk_counts.items():
        html += f"<li style='color:{RISK_LEVELS.get(risk, '#ccc')}'><b>{risk}:</b> {count}</li>"
    html += "</ul>"
    html += generate_legend_html()
    html += "<h2>Findings</h2><table border=1 cellpadding=5><tr><th>Test</th><th>Plugin</th><th>Risk</th><th>References</th><th>Result/Details</th><th>Recommended Fix</th></tr>"
    for r in results:
        refs = [INDUSTRY_REFERENCES.get(ref, ref) for ref in r.get("references",[])]
        risk = r.get("risk", "Unknown")
        html += (
            "<tr>"
            f"<td>{r['scenario'].get('name','')}</td>"
            f"<td>{r.get('plugin','')}</td>"
            f"<td style='color:{RISK_LEVELS.get(risk, '#ccc')}'>{risk}</td>"
            f"<td>{', '.join(refs)}</td>"
            f"<td><pre>{json.dumps(r.get('result',r.get('error','')),indent=2)}</pre></td>"
            f"<td>{FIX_GUIDES.get(risk,'')}</td>"
            "</tr>"
        )
    html += "</table>"
    html += "<h2>Glossary & Industry References</h2><ul>"
    html += "<li><b>Critical:</b> Immediate action. Example: Prompt injection response (OWASP LLM01).</li>"
    html += "<li><b>High:</b> High business/security risk. Exfiltration not blocked.</li>"
    html += "<li><b>Medium:</b> Advisory. Model memory/context loss detected.</li>"
    html += "<li><b>Low:</b> Minor/edge issue. Monitor and update.</li>"
    html += "<li><b>Pass:</b> No risk detected.</li>"
    html += "<li><b>Unknown:</b> New or unclassified risk.</li>"
    html += "</ul><hr>"
    html += "<small>Report auto-generated by AI Test Suite v2. For audit/compliance, consult LLM security benchmarks (OWASP, NIST, OpenAI Evals, Anthropic Playbook).</small>"
    html += "</body></html>"
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
