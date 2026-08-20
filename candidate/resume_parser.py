"""Resume text extraction for PDF and DOCX files.

DOCX resumes are often designed with tables/columns.  Reading only
``Document.paragraphs`` misses almost the entire resume in those cases, which
caused ATS scores to become 0% even when the skills were clearly present.
"""

from pathlib import Path

try:
    import fitz
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PyMuPDF is not installed. Run: python -m pip install -r requirements.txt"
    ) from exc

from docx import Document


def _clean_piece(value):
    value = (value or "").replace("\r", "\n")
    lines = []
    for line in value.splitlines():
        line = " ".join(line.split())
        if line:
            lines.append(line)
    return "\n".join(lines)


def _extract_table(table, output):
    for row in table.rows:
        for cell in row.cells:
            cell_text = _clean_piece(cell.text)
            if cell_text:
                output.append(cell_text)
            # Support nested tables used by some resume templates.
            for nested in cell.tables:
                _extract_table(nested, output)


def extract_text_from_pdf(file_path):
    """Extract readable text from every page of a PDF resume."""
    chunks = []
    document = fitz.open(str(file_path))
    try:
        for page in document:
            text = page.get_text("text")
            if text:
                chunks.append(text)
    finally:
        document.close()
    return "\n".join(chunks).strip()


def extract_text_from_docx(file_path):
    """Extract paragraphs AND table/cell content from a DOCX resume.

    Many professional resumes put all content inside a two-column table.  The
    old parser only read paragraphs, so it returned almost-empty text.
    """
    document = Document(str(file_path))
    chunks = []

    for paragraph in document.paragraphs:
        text = _clean_piece(paragraph.text)
        if text:
            chunks.append(text)

    for table in document.tables:
        _extract_table(table, chunks)

    # De-duplicate exact chunks while preserving document order.
    seen = set()
    unique = []
    for chunk in chunks:
        key = chunk.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(chunk.strip())

    return "\n".join(unique).strip()


def extract_resume_text(file_path):
    """Detect the file type and extract text without changing the real path."""
    path = Path(str(file_path))
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    raise ValueError("Unsupported resume format. Only PDF and DOCX are supported.")
