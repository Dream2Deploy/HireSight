import streamlit as st
import pandas as pd
import plotly.express as px
from backend.resume_parser import extract_text, normalize_text, extract_skills_from_resume
from backend.jd_parser import parse_jd
from backend.matcher import final_score, generate_feedback
from backend.db import init_db, save_evaluation, fetch_all
import os
import streamlit as st
st.set_page_config(page_title="Resume Relevance Checker", layout="wide")

st.write("✅ App started running...")


# Initialize DB
init_db()

# Page config
st.set_page_config(page_title="Resume Relevance Checker", layout="wide")

# Sidebar Navigation
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📊 Evaluate", "📑 Bulk Ranking", "📜 History"])


st.title("⚡ Automated Resume Relevance Checker")
st.caption("Hackathon Project | Innomatics Research Labs")

if page == "🏠 Home":
    st.markdown("### Welcome!")
    st.write("""
    This tool helps match **Resumes** against **Job Descriptions** automatically.
    
    **Features:**
    - Parse resumes & job descriptions (PDFs)
    - Detect technical skills
    - Match against job requirements
    - Score relevance (hard + semantic)
    - Generate improvement suggestions
    - Store & browse evaluations
    """)
    st.success("👉 Go to '📊 Evaluate' from the sidebar to start.")

elif page == "📊 Evaluate":
    st.subheader("📂 Upload Resume & JD")

    # File uploads
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    jd_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"])

    if resume_file and jd_file:
        # Save temp files
        resume_path = "temp_resume.pdf"
        jd_path = "temp_jd.pdf"

        with open(resume_path, "wb") as f:
            f.write(resume_file.read())
        with open(jd_path, "wb") as f:
            f.write(jd_file.read())

        # Extract text
        resume_text = normalize_text(extract_text(resume_path))
        jd_text = normalize_text(extract_text(jd_path))

        # Parse JD
        jd_parsed = parse_jd(jd_text, file_path=jd_path)

        # Extract resume skills
        resume_skills = extract_skills_from_resume(resume_text)

        # Final scoring
        result = final_score(resume_skills, jd_parsed, resume_text, jd_text)

        # Feedback
        feedback = generate_feedback(jd_parsed, result)

        # --- Display Results ---
        st.subheader("📊 Evaluation Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("Hard Match Score", f"{result['hard_score']}%")
        col2.metric("Semantic Similarity", f"{result['soft_score']}%")
        col3.metric("Final Relevance", f"{result['final_score']}% ({result['verdict']})")

        st.progress(int(result["final_score"]))

        # Pie Chart for skills
        matched = len(resume_skills)
        missing = len(result["missing_must"]) + len(result["missing_good"])
        fig = px.pie(
            names=["Matched Skills", "Missing Skills"],
            values=[matched, missing],
            color=["Matched Skills", "Missing Skills"],
            color_discrete_map={"Matched Skills": "green", "Missing Skills": "red"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Expandable Sections
        with st.expander("📄 Resume Extract"):
            st.text(resume_text[:1000] + " ...")

        with st.expander("📝 Job Description Extract"):
            st.text(jd_text[:1000] + " ...")

        with st.expander("✅ Parsed Job Requirements"):
            st.json(jd_parsed)

        with st.expander("💡 Suggestions for Improvement"):
            st.write(feedback)

        # Save to DB
        if st.button("💾 Save Evaluation"):
            save_evaluation(
                candidate_name="Candidate",
                resume_file=resume_file.name,
                jd_file=jd_file.name,
                result=result,
                feedback=feedback
            )
            st.success("Evaluation saved to database!")

elif page == "📜 History":
    st.subheader("📜 Previous Evaluations")
    rows = fetch_all()
    if rows:
        df = pd.DataFrame(rows, columns=[
            "ID", "Timestamp", "Candidate", "Resume", "JD",
            "Final Score", "Hard Score", "Soft Score", "Verdict",
            "Missing Skills", "Feedback"
        ])
        st.dataframe(df)
    else:
        st.info("No evaluations found yet. Run one from 📊 Evaluate.")

elif page == "📑 Bulk Ranking":
    st.subheader("📑 Bulk Resume Ranking")

    jd_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"], key="bulk_jd")
    resume_files = st.file_uploader(
        "Upload Multiple Resumes (PDFs)", type=["pdf"], accept_multiple_files=True, key="bulk_resumes"
    )

    if jd_file and resume_files:
        # Save JD
        jd_path = "temp_bulk_jd.pdf"
        with open(jd_path, "wb") as f:
            f.write(jd_file.read())

        jd_text = normalize_text(extract_text(jd_path))
        jd_parsed = parse_jd(jd_text, file_path=jd_path)

        results = []
        for resume_file in resume_files:
            # Save each resume temporarily
            resume_path = f"temp_{resume_file.name}"
            with open(resume_path, "wb") as f:
                f.write(resume_file.read())

            # Extract text & skills
            resume_text = normalize_text(extract_text(resume_path))
            resume_skills = extract_skills_from_resume(resume_text)

            # Score
            result = final_score(resume_skills, jd_parsed, resume_text, jd_text)

            results.append({
                "Candidate": resume_file.name,
                "Final Score": result["final_score"],
                "Verdict": result["verdict"],
                "Hard Score": result["hard_score"],
                "Soft Score": result["soft_score"],
                "Matched Skills": ", ".join(resume_skills),
                "Missing Skills": ", ".join(result["missing_must"] + result["missing_good"])
            })

        # Convert to DataFrame & sort
        df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)

        st.success("✅ Ranking Complete!")
        st.dataframe(df, use_container_width=True)

        # Download option
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Results as CSV", csv, "ranking_results.csv", "text/csv")
