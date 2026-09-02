import pymupdf as fitz
from docx import Document


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume.
    """

    text = ""

    document = fitz.open(file_path)

    for page in document:
        text += page.get_text()

    document.close()

    return text


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX resume.
    """

    text = ""

    document = Document(file_path)

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_resume_text(file_path):
    """
    Detect the file type and extract resume text.
    """

    file_path = str(file_path).lower()

    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    else:
        raise ValueError(
            "Unsupported resume format. Only PDF and DOCX are supported."
        )