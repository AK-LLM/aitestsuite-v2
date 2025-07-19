import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# You may want to further modularize for more metrics/benchmarks

def benchmark_result(plugin, result):
    # Example: basic check, can be extended with more logic
    critical = result.get("status", "").lower() in ["fail", "critical", "vulnerable"]
    recommendations = []
    if critical:
        recommendations.append("Immediate remediation recommended. See plugin docs.")
    else:
        recommendations.append("No critical issues found. Continue to monitor and test regularly.")
    # Add more industry standards/benchmarks as needed
    return critical, recommendations

def summarize_results(results):
    summary = {
        "total_tests": len(results),
        "critical_issues": 0,
        "passed": 0,
        "failed": 0,
        "details": [],
    }
    for plugin, result in results.items():
        critical, recommendations = benchmark_result(plugin, result)
        status = result.get("status", "").lower()
        if status in ["pass", "ok"]:
            summary["passed"] += 1
        else:
            summary["failed"] += 1
        if critical:
            summary["critical_issues"] += 1
        summary["details"].append({
            "plugin": plugin,
            "status": status,
            "details": result.get("details", ""),
            "recommendations": recommendations
        })
    return summary

def save_json_report(summary, output_path):
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

def save_pdf_report(summary, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    line_height = 18
    x_margin = 40
    y = height - 40

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x_margin, y, "AI Test Suite Report")
    y -= 2 * line_height

    c.setFont("Helvetica", 12)
    c.drawString(x_margin, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= line_height
    c.drawString(x_margin, y, f"Total Tests: {summary['total_tests']}")
    y -= line_height
    c.drawString(x_margin, y, f"Passed: {summary['passed']}  Failed: {summary['failed']}  Critical: {summary['critical_issues']}")
    y -= 2 * line_height

    for detail in summary["details"]:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, y, f"Plugin: {detail['plugin']}   Status: {detail['status'].upper()}")
        y -= line_height
        c.setFont("Helvetica", 10)
        c.drawString(x_margin + 10, y, f"Details: {detail['details']}")
        y -= line_height
        for rec in detail["recommendations"]:
            c.drawString(x_margin + 10, y, f"Recommendation: {rec}")
            y -= line_height
        y -= line_height // 2
        if y < 80:
            c.showPage()
            y = height - 40
    c.save()

def generate_full_report(results, output_dir="reports", base_filename="ai_test_report"):
    os.makedirs(output_dir, exist_ok=True)
    summary = summarize_results(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.json")
    pdf_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.pdf")
    save_json_report(summary, json_path)
    save_pdf_report(summary, pdf_path)
    return {"json": json_path, "pdf": pdf_path, "summary": summary}

# Example usage:
# results = {
#     "jailbreaks": {"status": "fail", "details": "Model was tricked by adversarial prompt"},
#     "context_leak": {"status": "pass", "details": "No context leak detected"},
# }
# paths = generate_full_report(results)
# print("Reports saved:", paths)
