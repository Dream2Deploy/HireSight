import os
import re

def parse_jd(jd_text: str, file_path: str = None) -> dict:
    """
    Parse a job description into structured fields.
    :param jd_text: raw text extracted from JD PDF
    :param file_path: path of JD file (optional, used for extension check)
    :return: dictionary with role title, must-have, good-to-have, and raw text
    """

    ext = os.path.splitext(file_path)[1].lower() if file_path else ""

    # Extract role title: first non-empty line
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    role_title = lines[0] if lines else "Unknown Role"

    must_have = []
    good_to_have = []

    # Heuristics for extracting requirements
    for line in lines:
        lower_line = line.lower()

        if "must" in lower_line or "requirement" in lower_line or "who you are" in lower_line:
            must_have.append(line)

        elif "good" in lower_line or "nice to have" in lower_line or "preferred" in lower_line:
            good_to_have.append(line)

        # Catch bullet points (●, -, etc.)
        elif line.startswith("●") or line.startswith("-") or re.match(r"^\d+\.", line):
            must_have.append(line)

    return {
        "role_title": role_title,
        "must_have": must_have,
        "good_to_have": good_to_have,
        "raw_text": jd_text
    }
