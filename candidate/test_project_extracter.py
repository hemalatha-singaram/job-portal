from django.test import SimpleTestCase
from .education_extracter import extract_education
from .project_extracter import extract_projects
from .certificate_extracter import extract_certificates


class ProjectEducationExtractorTests(SimpleTestCase):
    def test_empty_projects(self): self.assertEqual(extract_projects(""), "")
    def test_projects_section(self):
        self.assertIn("CampusHire", extract_projects("PROJECTS:\nCampusHire\nEDUCATION:\nB.Tech"))
    def test_projects_stop_at_next_section(self):
        self.assertNotIn("EDUCATION", extract_projects("PROJECTS\nProject A\nEDUCATION\nB.Tech"))
    def test_missing_heading(self): self.assertEqual(extract_projects("Built a project using Python."), "")
    def test_table_style_project_heading(self):
        self.assertIn("CampusHire", extract_projects("PROJECTS /\nCampusHire\nEDUCATION /\nB.Tech"))
    def test_certificates_section(self):
        result = extract_certificates("CERTIFICATIONS\nTata Group — GenAI Analytics | Forage | Feb 2026\nEDUCATION\nB.Tech")
        self.assertIn("Tata Group", result)
    def test_education_percentages(self):
        result = extract_education("10th - 92%\nIntermediate - 88%\nB.Tech - 82%")
        self.assertEqual(result["tenth_percentage"], 92.0)
        self.assertEqual(result["intermediate_percentage"], 88.0)
        self.assertEqual(result["graduation_percentage"], 82.0)
    def test_graduation_cgpa(self): self.assertEqual(extract_education("B.Tech - CGPA: 8.4")["graduation_cgpa"], 8.4)
