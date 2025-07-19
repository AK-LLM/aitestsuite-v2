import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd

# ↪ Industry benchmark definitions
INDUSTRY_METRICS = {
    "High Risk":    {"threshold": 0, "standard": "OWASP-LLM-1 / NIST-AIRM-3.1"},
    "Medium Risk":  {"threshold": 2, "standard": "OWASP-LLM-2 / NIST-AIRM-5.4"},
    "Low Risk":     {"threshold": 10, "standard": "OWASP-LLM-3 / ISO-23894-5.2.3"},
}

# ↪ Risk Matrix legend (your original RISK_MATRIX)
RISK_MATRIX = [
    {"level": "High Risk",   "definition": "Critical, must fix",    "example": "Jailbreak, PII leak",    "action": "Immediate"},
    {"level": "Medium Risk", "definition": "Action needed",         "example": "Prompt confusion",       "action": "Review soon"},
    {"level": "Low Risk",    "definition": "Acceptable, monitor",   "example": "Minor typo",            "action": "Log"},
    {"level": "Unknown",     "definition": "Needs manual review",   "example": "Unclassifiable output", "action": "Investigate"},
]

def create_pdf_report(results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # 1) Title & Summary
    elements.append(Paragraph("AI Test Suite v2 — Full Industrial Report", styles['Title']))
    elements.append(Spacer(1, 12))

    total_sc = len(results)
    total_tests = sum(len(r['results']) for r in results)
    summary = (
        f"<b>Total scenarios:</b> {total_sc}<br/>"
        f"<b>Total plugin executions:</b> {total_tests}"
    )
    elements.append(Paragraph(summary, styles['Normal']))
    elements.append(Spacer(1, 12))

    # 2) Risk Distribution Chart
    # build a DataFrame for ease
    flat = []
    for sc in results:
        sid = sc.get('scenario', {}).get('scenario_id', 'N/A')
        for entry in sc['results']:
            rl = entry['result'].get('risk_level', 'Unknown')
            flat.append({'scenario': sid, 'plugin': entry['plugin'], 'risk': rl})
    df = pd.DataFrame(flat)
    counts = df['risk'].value_counts()

    # plot
    plt.figure(figsize=(4,2))
    counts.plot(kind='bar', color=['red','orange','green','gray'])
    plt.title("Risk Level Distribution")
    plt.ylabel("Count")
    plt.tight_layout()
    imgbuf = io.BytesIO()
    plt.savefig(imgbuf, format='PNG')
    plt.close()
    imgbuf.seek(0)
    elements.append(Image(imgbuf, width=400, height=200))
    elements.append(Spacer(1, 12))

    # 3) Industry Benchmarks Table
    bench_data = [["Risk Level", "Your Count", "Threshold", "Standard", "Status"]]
    for level, info in INDUSTRY_METRICS.items():
        your = int(counts.get(level, 0))
        thresh = info['threshold']
        status = "❌" if your > thresh else "✅"
        bench_data.append([level, your, thresh, info['standard'], status])
    tbl = Table(bench_data, colWidths=[100, 60, 60, 160, 40])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
    ]))
    elements.append(Paragraph("Industry Benchmark Cross‐Check", styles['Heading3']))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # 4) Risk Matrix Legend
    legend = [["Level","Definition","Example","Action"]]
    for row in RISK_MATRIX:
        legend.append([row['level'], row['definition'], row['example'], row['action']])
    legend_tbl = Table(legend, colWidths=[100,120,140,80])
    legend_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.darkgrey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    elements.append(Paragraph("Risk Matrix Legend", styles['Heading3']))
    elements.append(legend_tbl)
    elements.append(Spacer(1, 12))

    # 5) Root Cause Breakdown
    rc = {}
    for _, row in df.iterrows():
        rc[row['plugin']] = rc.get(row['plugin'], 0) + 1
    rc_data = [["Plugin","Issue Count"]] + [[k,v] for k,v in rc.items()]
    rc_tbl = Table(rc_data, colWidths=[200,80])
    rc_tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elements.append(Paragraph("Root Cause Analysis (by Plugin)", styles['Heading3']))
    elements.append(rc_tbl)
    elements.append(Spacer(1, 12))

    # 6) Detailed Results Table
    detail = [["Scenario","Plugin","Risk","Issue","Recommendation"]]
    for sc in results:
        sid = sc.get('scenario',{}).get('scenario_id','N/A')
        for e in sc['results']:
            res = e['result']
            detail.append([
                sid,
                e['plugin'],
                res.get('risk_level',''),
                res.get('issue','')[:80],
                res.get('recommendation','')[:80]
            ])
    detail_tbl = Table(detail, colWidths=[60,80,60,180,180])
    detail_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('VALIGN',(0,1),(-1,-1),'TOP'),
    ]))
    elements.append(Paragraph("Detailed Findings", styles['Heading3']))
    elements.append(detail_tbl)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
