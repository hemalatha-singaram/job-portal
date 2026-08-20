from pathlib import Path
from tempfile import TemporaryDirectory
from django.test import SimpleTestCase
from docx import Document
from .resume_parser import extract_resume_text


class ResumeParserTests(SimpleTestCase):
    def test_unsupported_extension(self):
        with self.assertRaises(ValueError): extract_resume_text("resume.txt")
    def test_missing_pdf_is_rejected_by_reader(self):
        with self.assertRaises(Exception): extract_resume_text("missing.pdf")
    def test_missing_docx_is_rejected_by_reader(self):
        with self.assertRaises(Exception): extract_resume_text("missing.docx")
    def test_docx_text_is_extracted(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.docx"; doc = Document(); doc.add_paragraph("Python Django SQL"); doc.save(path)
            self.assertIn("Python Django SQL", extract_resume_text(path))

    def test_docx_table_text_is_extracted(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "table_resume.docx"
            doc = Document()
            table = doc.add_table(rows=1, cols=1)
            table.cell(0, 0).text = "TECHNICAL SKILLS\nPython, SQL, Git\nPROJECTS\nCampusHire"
            doc.save(path)
            text = extract_resume_text(path)
            self.assertIn("TECHNICAL SKILLS", text)
            self.assertIn("CampusHire", text)
