
import re

SKILLS_LIST = [
    "python", "java", "c", "c++", "sql", "excel",
    "power bi", "pandas", "numpy", "machine learning",
    "deep learning", "html", "css", "javascript",
    "react", "django", "flask", "git", "github",
    "data analysis", "statistics", "tensorflow",
    "scikit-learn", "communication", "problem solving"
]

def preprocess_text(text):
    """Convert resume text into a consistent format."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    return text.strip()

def detect_skills(text):
    """Identify skills mentioned in the resume."""

    clean_text = preprocess_text(text)
    detected = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, clean_text):
            detected.append(skill)

    return detected

def detect_experience(text):
    """Find experience-related information."""

    experience_keywords = [
        "experience", "internship", "intern",
        "work history", "professional experience",
        "worked at", "employment"
    ]

    lines = text.splitlines()
    experience_lines = []

    for line in lines:
        if any(word in line.lower() for word in experience_keywords):
            if line.strip():
                experience_lines.append(line.strip())

    if experience_lines:
        return "\n".join(experience_lines)

    return "No clear experience or internship details detected."

def calculate_resume_score(text, skills):
    """Calculate a simple rule-based resume score out of 100."""

    clean_text = preprocess_text(text)
    score = 0

    # Skills: 25 marks
    if skills:
        score += min(25, len(skills) * 5)

    # Education: 20 marks
    if any(word in clean_text for word in [
        "education", "degree", "bachelor", "bca",
        "b.tech", "bachelor of computer applications"
    ]):
        score += 20

    # Projects: 20 marks
    if any(word in clean_text for word in [
        "project", "projects", "developed", "built"
    ]):
        score += 20

    # Experience: 20 marks
    if any(word in clean_text for word in [
        "experience", "internship", "intern",
        "work history", "professional experience"
    ]):
        score += 20

    # Resume completeness: 15 marks
    contact_found = (
        re.search(r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b", text)
        or re.search(r"\b\d{10}\b", text)
    )

    if contact_found:
        score += 15

    return min(score, 100)

def generate_tips(text, skills):
    """Generate basic resume improvement tips."""

    clean_text = preprocess_text(text)
    tips = []

    if not skills:
        tips.append("Add relevant technical and professional skills.")
    elif len(skills) < 5:
        tips.append("Include more relevant skills that you actually possess.")

    if "education" not in clean_text and "degree" not in clean_text:
        tips.append("Add a clearly labelled Education section.")

    if "project" not in clean_text:
        tips.append("Include projects with technologies and your contributions.")

    if not any(word in clean_text for word in [
        "experience", "internship", "intern"
    ]):
        tips.append(
            "Add relevant internship or work experience if available."
        )

    if not re.search(r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b", text):
        tips.append("Include a professional email address.")

    if not tips:
        tips.append(
            "Your resume contains the basic sections checked by this system. "
            "Review formatting, grammar, achievements and job-specific keywords."
        )

    return tips

def analyze_resume(text):
    """Run all resume analysis functions."""

    skills = detect_skills(text)
    experience = detect_experience(text)
    score = calculate_resume_score(text, skills)
    tips = generate_tips(text, skills)

    return {
        "skills": skills,
        "experience": experience,
        "score": score,
        "tips": tips
    }