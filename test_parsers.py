from backend.resume_parser import extract_text, normalize_text, extract_skills_from_resume
from backend.jd_parser import parse_jd
from backend.matcher import hard_match, semantic_similarity, final_score, generate_feedback
from backend.db import init_db, save_evaluation, fetch_all

# Paths to sample data
resume_path = "Sample_Data/resumes/Resume - 1.pdf"
jd_path = "Sample_Data/job_descriptions/sample_jd_1.pdf"

# --- Extract Resume & JD ---
resume_text = normalize_text(extract_text(resume_path))
jd_text = normalize_text(extract_text(jd_path))

print("\n=== Resume Extract (first 300 chars) ===")
print(resume_text[:300])

print("\n=== JD Extract (first 300 chars) ===")
print(jd_text[:300])

# --- Parse JD ---
jd_parsed = parse_jd(jd_text, file_path=jd_path)
print("\n=== Parsed JD ===")
print(jd_parsed)

# --- Extract Resume Skills ---
resume_skills = extract_skills_from_resume(resume_text)
print("\n=== Skills Detected in Resume ===")
print(resume_skills)

# --- Final Scoring ---
final_result = final_score(resume_skills, jd_parsed, resume_text, jd_text)
print("\n=== Final Relevance Score ===")
print(final_result)

# --- Feedback ---
feedback = generate_feedback(jd_parsed, final_result)
print("\n=== Suggestions for Improvement ===")
print(feedback)

# --- Save to DB ---
init_db()
save_evaluation(
    candidate_name="Pavan Kalyan",
    resume_file=resume_path,
    jd_file=jd_path,
    result=final_result,
    feedback=feedback
)

print("\n=== Saved to Database ===")

rows = fetch_all()
print("\n=== All DB Records ===")
for row in rows:
    print(row)
