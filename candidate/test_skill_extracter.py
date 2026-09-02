from django.test import SimpleTestCase

from .skill_extracter import extract_skills


class SkillExtractorTests(SimpleTestCase):
    def test_empty_text_returns_empty(self): self.assertEqual(extract_skills(""), [])
    def test_none_returns_empty(self): self.assertEqual(extract_skills(None), [])
    def test_extracts_common_skills(self): self.assertEqual(extract_skills("Python, Django, SQL"), ["Python", "Django", "SQL"])
    def test_case_insensitive(self): self.assertIn("Python", extract_skills("PYTHON"))
    def test_multiline_text(self): self.assertIn("Machine Learning", extract_skills("Skills:\nMachine Learning\nGit"))
    def test_unknown_terms_are_ignored(self): self.assertEqual(extract_skills("Cooking Gardening"), [])
    def test_no_duplicate_skills(self): self.assertEqual(extract_skills("Python Python PYTHON").count("Python"), 1)
    def test_specialized_skills(self):
        result = extract_skills("PyTorch TensorFlow PostgreSQL")
        self.assertTrue(all(x in result for x in ["PyTorch", "TensorFlow", "PostgreSQL"]))
