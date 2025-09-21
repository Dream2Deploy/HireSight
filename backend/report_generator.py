from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(candidate_name, resume_file, jd_file, result, feedback, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    heading_style = styles["Heading2"]

    # Title
    elements.append(Paragraph(f"Resume Evaluation Report", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Candidate: {candidate_name}", normal_style))
    elements.append(Paragraph(f"Resume File: {resume_file}", normal_style))
    elements.append(Paragraph(f"Job Description File: {jd_file}", normal_style))
    elements.append(Spacer(1, 12))

    # Scores
    elements.append(Paragraph("📊 Scores", heading_style))
    score_data = [
        ["Final Score", f"{result['final_score']}%"],
        ["Hard Match", f"{result['hard_score']}%"],
        ["Semantic Match", f"{result['soft_score']}%"],
        ["Verdict", result["verdict"]]
    ]
    table = Table(score_data, colWidths=[150, 250])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica")
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Skills
    elements.append(Paragraph("✅ Matched Skills", heading_style))
    elements.append(Paragraph(", ".join(result["resume_skills"]) or "None", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("❌ Missing Skills", heading_style))
    elements.append(Paragraph(", ".join(result["missing_must"] + result["missing_good"]) or "None", normal_style))
    elements.append(Spacer(1, 12))

    # Feedback
    elements.append(Paragraph("💡 Suggestions for Improvement", heading_style))
    elements.append(Paragraph(feedback.replace("\n", "<br/>"), normal_style))

    # Save PDF
    doc.build(elements)
    return output_path
