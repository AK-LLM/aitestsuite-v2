# core/generate_report.py

import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# Mapped industry standards for each risk type/category
INDUSTRY_METRICS = {
    "Jailbreak": {"standard": "OWASP-LLM-1, NIST-AIRM-3.1", "threshold": 1, "desc": "Prompt injection/jailbreak resilience"},
    "Prompt Injection": {"standard": "OWASP-LLM-2, NIST-AIRM-5.4", "threshold": 1, "desc": "Injection/confusion attacks"},
    "Fuzzing": {"standard": "OWASP-LLM-3, ISO-23894 5.2.3", "threshold": 0, "desc": "Malformed input/robustness"},
    "Unicode/Obfuscation": {"standard": "OWASP-LLM-7", "threshold": 0, "desc": "Obfuscation/Unicode trick resilience"},
    "Context Leak": {"standard": "OWASP-LLM-4, NIST-AIRM-2.1", "threshold": 0, "desc": "Context/memory leak protection"},
    "Load/Stress": {"standard": "ISO-23894 7.3", "threshold": 0, "desc": "Load/rate limit resilience"},
    "Code/PII": {"standard": "OWASP-LLM-5, NIST-AIRM-3.2", "threshold": 0, "desc": "PII/code/secret exfil"},
    "Chain-of-Thought": {"standard": "OWASP-LLM-6", "threshold": 0, "desc": "Reasoning/trace leak protection"},
    "Bias/Toxicity": {"standard": "ISO-23894 6.4, NIST-AIRM-7.1", "threshold": 0, "desc": "Bias/toxic output filtering"},
    "Steganography": {"standard": "Custom/Advanced", "threshold": 0, "desc": "Stego/covert channel detection"},
    "Function Abuse": {"standard": "OWASP-LLM-8", "threshold": 0, "desc": "Tool/function misuse/hijack"},
    "Hallucination": {"standard": "OWASP-LLM-10, NIST-AIRM-4.2", "threshold": 0, "desc": "Factuality/hallucination"},
    "Role/Identity": {"standard": "Custom/Advanced", "threshold": 0, "desc": "Identity/role confusion"},
    "Other": {"standard": "-", "threshold": 0, "desc": "Other (see evidence)"},
}

def flatten_plugin_results(results):
    """Flatten complex plugin output to a row-based list for tables/export."""
    rows = []
    for res in results:
        # Per-plugin output
        if isinstance(res, dict):
            if "plugin" in res:
                # From chain runner: plugin, then result
                plugin = res["plugin"].replace(".py", "")
                out = res.get("out", {})
                if isinstance(out, dict):
                    rows.append({
                        "plugin": plugin,
                        "risk_level": out.get("risk_level"),
                        "issue": out.get("issue"),
                        "evidence": str(out.get("evidence", ""))[:500],
                        "recommendation": out.get("recommendation", ""),
                        "industry_standard": get_industry_ref(plugin)
                    })
                else:
                    # Error/exception
                    rows.append({
                        "plugin": plugin,
                        "risk_level": "Error",
                        "issue": str(out),
                        "evidence": "",
                        "recommendation": "Check plugin or API error.",
                        "industry_standard": get_industry_ref(plugin)
                    })
            else:
                # Direct plugin output
                plugin = res.get("plugin", "Unknown")
                rows.append({
                    "plugin": plugin,
                    "risk_level": res.get("risk_level"),
                    "issue": res.get("issue"),
                    "evidence": str(res.get("evidence", ""))[:500],
                    "recommendation": res.get("recommendation", ""),
                    "industry_standard": get_industry_ref(plugin)
                })
        else:
            # Unexpected structure
            rows.append({"plugin": "Unknown", "risk_level": "Unknown", "issue": str(res), "evidence": "", "recommendation": "", "industry_standard": ""})
    return rows

def get_industry_ref(plugin_name):
    """Guess best industry reference for a plugin type."""
    for k, v in INDUSTRY_METRICS.items():
        if k.lower() in plugin_name.lower():
            return f"{v['standard']} ({v['desc']})"
    return "Other"

def generate_report(results, filename="AI_Test_Report.pdf"):
    """Generate a PDF report for the results (handles any plugin, any output structure)."""
    # Flatten all results into rows
    if isinstance(results, dict) and "results" in results:
        flat = flatten_plugin_results(results["results"])
    elif isinstance(results, list):
        flat = flatten_plugin_results(results)
    else:
        flat = []
    df = pd.DataFrame(flat)
    # ---- PDF generation ----
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "AI Red Team Test Suite: Industrial-Grade Report")

    y = height - 90
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Benchmarked against OWASP LLM Top 10, NIST AI RMF, ISO/IEC 23894, others.")
    y -= 20

    # Table header
    table_data = [["Plugin", "Risk", "Industry Ref", "Issue", "Recommendation"]]
    for _, row in df.iterrows():
        table_data.append([
            str(row["plugin"]),
            str(row["risk_level"]),
            str(row["industry_standard"]),
            str(row["issue"])[:70],
            str(row["recommendation"])[:60]
        ])
    # Table style
    table = Table(table_data, colWidths=[80, 50, 120, 160, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    table.wrapOn(c, width, height)
    table_height = 20 * len(table_data)
    table.drawOn(c, 40, max(60, y - table_height))

    # Root cause/risk chart: bar chart of risk levels
    risk_counts = df["risk_level"].value_counts().to_dict()
    chart_y = max(60, y - table_height) - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, chart_y, "Risk Level Distribution:")
    c.setFont("Helvetica", 10)
    for i, (risk, count) in enumerate(risk_counts.items()):
        c.drawString(60, chart_y - (i + 1) * 15, f"{risk}: {count}")

    # Industry benchmarking summary
    summary_y = chart_y - (len(risk_counts) + 1) * 15 - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, summary_y, "Industry Benchmarking (see OWASP/NIST references):")
    c.setFont("Helvetica", 10)
    for i, (k, v) in enumerate(INDUSTRY_METRICS.items()):
        c.drawString(60, summary_y - (i + 1) * 13, f"{k}: max allowed risk: {v['threshold']} | {v['standard']}")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# If using in Streamlit:
# st.download_button("Download PDF Report", data=generate_report(results), file_name="AI_Test_Report.pdf")
# Or for CSV/JSON:
# pd.DataFrame(flatten_plugin_results(results)).to_csv("ai_report.csv", index=False)
