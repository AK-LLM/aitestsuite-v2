# File: core/generate_report.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd

# Industry benchmark definitions
INDUSTRY_METRICS = {
    "High Risk":    {"threshold": 0, "standard": "OWASP-LLM-1 / NIST-AIRM-3.1"},
    "Medium Risk":  {"threshold": 2, "standard": "OWASP-LLM-2 / NIST-AIRM-5.4"},
    "Low Risk":     {"threshold": 10, "standard": "OWASP-LLM-3 / ISO-23894-5.2.3"},
}

# Risk matrix legend
RISK_MATRIX = [
    {"level": "High Risk",   "definition": "Critical, must fix",    "example": "Jailbreak, PII leak",    "action": "Immediate"},
    {"level": "Medium Risk", "definition": "Action needed",         "example": "Prompt confusion",       "action": "Review soon"},
    {"level": "Low Risk",    "definition": "Acceptable, monitor",   "example": "Minor typo",            "action": "Log"},
    {"level": "Unknown",     "definition": "Needs manual review",   "example": "Unclassifiable output", "action": "Investigate"},
]

def create_pdf_report(results):
    """
    Generates a comprehensive PDF report for the given test results.

    Args:
        results (list): A list of scenario dicts, each containing:
            - 'scenario': dict with 'scenario_id'
            - 'results': list of plugin test dicts with 'plugin' and 'result'

    Returns:
        io.BytesIO: PDF binary buffer ready for streaming/download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # 1) Title & Summary
    elements.append(Paragraph("AI Test Suite v2 — Comprehensive Report", styles['Title']))
    elements.append(Spacer(1, 12))
    total_scenarios = len(results)
    total_tests = sum(len(item['results']) for item in results)
    summary = (
        f"<b>Total scenarios tested:</b> {total_scenarios}<br/>"
        f"<b>Total plugin executions:</b> {total_tests}"
    )
    elements.append(Paragraph(summary, styles['Normal']))
    elements.append(Spacer(1, 12))

    # 2) Flatten into DataFrame for charts and tables
    records = []
    for scenario in results:
        sid = scenario.get('scenario', {}).get('scenario_id', 'N/A')
        for entry in scenario['results']:
            plugin = entry['plugin']
            res = entry['result']
            rl = res.get('risk_level', 'Unknown')
            records.append({'scenario': sid, 'plugin': plugin, 'risk': rl})
    df = pd.DataFrame(records)
    risk_counts = df['risk'].value_counts()

    # 3) Risk Distribution Chart
    plt.figure(figsize=(4,2))
    risk_counts.plot(kind='bar', color=['red','orange','green','gray'])
    plt.title("Risk Level Distribution")
    plt.ylabel("Count")
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)
    elements.append(Image(img_buffer, width=400, height=200))
    elements.append(Spacer(1, 12))

    # 4) Industry Benchmark Table
    bench_data = [["Risk Level","Your Count","Threshold","Standard","Status"]]
    for level, info in INDUSTRY_METRICS.items():
        count = int(risk_counts.get(level, 0))
        thresh = info['threshold']
        status = "❌" if count > thresh else "✅"
        bench_data.append([level, count, thresh, info['standard'], status])
    bench_tbl = Table(bench_data, colWidths=[100,60,60,160,40])
    bench_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
    ]))
    elements.append(Paragraph("Industry Benchmark Cross-Check", styles['Heading3']))
    elements.append(bench_tbl)
    elements.append(Spacer(1, 12))

    # 5) Risk Matrix Legend
    legend_data = [["Level","Definition","Example","Action"]]
    for row in RISK_MATRIX:
        legend_data.append([row['level'], row['definition'], row['example'], row['action']])
    legend_tbl = Table(legend_data, colWidths=[100,120,140,80])
    legend_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.darkgrey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    elements.append(Paragraph("Risk Matrix Legend", styles['Heading3']))
    elements.append(legend_tbl)
    elements.append(Spacer(1, 12))

    # 6) Root Cause Analysis (Plugin counts)
    root_counts = df['plugin'].value_counts().reset_index().values.tolist()
    root_data = [["Plugin","Issue Count"]] + root_counts
    root_tbl = Table(root_data, colWidths=[200,80])
    root_tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elements.append(Paragraph("Root Cause Analysis by Plugin", styles['Heading3']))
    elements.append(root_tbl)
    elements.append(Spacer(1, 12))

    # 7) Detailed Findings Table
    detail_data = [["Scenario","Plugin","Risk","Issue","Recommendation"]]
    for scenario in results:
        sid = scenario.get('scenario', {}).get('scenario_id', 'N/A')
        for entry in scenario['results']:
            plugin = entry['plugin']
            res = entry['result']
            issue = res.get('issue','-')
            rec = res.get('recommendation','-')
            detail_data.append([sid, plugin, res.get('risk_level','-'), issue, rec])
    detail_tbl = Table(detail_data, colWidths=[60,80,60,180,180])
    detail_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('VALIGN',(0,1),(-1,-1),'TOP'),
    ]))
    elements.append(Paragraph("Detailed Findings", styles['Heading3']))
    elements.append(detail_tbl)

    # Build and return PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
