from sentence_transformers import SentenceTransformer, util

# Load model once (avoid reloading on every function call)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def hard_match(resume_text: str, jd_parsed: dict) -> dict:
    """
    Rule-based matching of resume against JD requirements.
    """
    resume_text_lower = resume_text.lower()
    must_have = jd_parsed.get("must_have", [])
    good_to_have = jd_parsed.get("good_to_have", [])

    must_matched = [req for req in must_have if req.lower() in resume_text_lower]
    good_matched = [req for req in good_to_have if req.lower() in resume_text_lower]

    missing_must = [req for req in must_have if req.lower() not in resume_text_lower]
    missing_good = [req for req in good_to_have if req.lower() not in resume_text_lower]

    # Simple scoring rule
    score = (len(must_matched) * 5 + len(good_matched) * 2) / max(
        1, (len(must_have) * 5 + len(good_to_have) * 2)
    ) * 100

    return {
        "score": round(score, 2),
        "must_matched": must_matched,
        "good_matched": good_matched,
        "missing_must": missing_must,
        "missing_good": missing_good,
    }


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Semantic similarity between resume and job description using embeddings.
    """
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(resume_emb, jd_emb).item()
    return round(similarity * 100, 2)


def final_score(resume_skills: list, jd_parsed: dict, resume_text: str, jd_text: str) -> dict:
    """
    Combine hard and semantic matching for a final weighted score.
    """
    hard_result = hard_match(resume_text, jd_parsed)
    soft_score = semantic_similarity(resume_text, jd_text)

    # Weighted final score (50% hard, 50% soft)
    final = (hard_result["score"] * 0.5) + (soft_score * 0.5)

    verdict = "High" if final >= 70 else "Medium" if final >= 50 else "Low"

    return {
        "resume_skills": resume_skills,
        "hard_score": hard_result["score"],
        "soft_score": soft_score,
        "final_score": round(final, 2),
        "verdict": verdict,
        "missing_must": hard_result["missing_must"],
        "missing_good": hard_result["missing_good"],
    }


def generate_feedback(jd_parsed: dict, match_result: dict) -> str:
    """
    Generate actionable feedback for the candidate.
    """
    missing = match_result.get("missing_must", []) + match_result.get("missing_good", [])

    suggestions = []
    if missing:
        suggestions.append("⚡ Add or highlight these skills/projects in your resume: " + ", ".join(missing[:8]))
    suggestions.append("📌 Include measurable results in projects (e.g., 'improved accuracy by 10%').")
    suggestions.append("📌 Move Technical Skills section to the top for better visibility.")
    suggestions.append("📌 Add certifications or online courses for missing skills if possible.")
    suggestions.append("📌 Include links to GitHub/portfolio to showcase hands-on projects.")

    return "\n".join(suggestions)
