

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