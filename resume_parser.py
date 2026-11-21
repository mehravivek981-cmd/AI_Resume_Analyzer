import re
from PyPDF2 import PdfReader


def extract_resume_text(file_path):
    """Extract text from a PDF resume."""

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError(
            "No readable text found. Please upload a text-based PDF resume."
        )

    return text


_NOT_A_NAME = (
    "resume", "curriculum", "vitae", "cv", "profile", "objective",
    "summary", "contact", "email", "phone", "address", "education",
    "skills", "experience", "projects", "linkedin", "github",
)


def extract_candidate_name(text):
    """Guess the candidate's name from the top of the resume."""

    for line in text.splitlines()[:12]:
        line = line.strip()

        if not line or "@" in line or any(ch.isdigit() for ch in line):
            continue

        if any(word in line.lower() for word in _NOT_A_NAME):
            continue

        words = line.split()

        if 2 <= len(words) <= 4 and all(
            re.fullmatch(r"[A-Za-z.'-]+", w) for w in words
        ):
            return line.title() if line.isupper() else line

    # Fallback: build a name from the email address
    email = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    if email:
        local = re.sub(r"\d+", "", email.group(0).split("@")[0])
        parts = [p for p in re.split(r"[._+-]+", local) if p]
        if parts:
            return " ".join(p.capitalize() for p in parts)

    return "Candidate"
