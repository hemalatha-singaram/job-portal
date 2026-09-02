from django.test import SimpleTestCase
from .experience_extracter import extract_experience


class ExperienceExtractorTests(SimpleTestCase):
    def test_empty(self): self.assertEqual(extract_experience(""), 0)
    def test_none(self): self.assertEqual(extract_experience(None), 0)
    def test_years(self): self.assertEqual(extract_experience("3 years experience"), 3)
    def test_highest_year(self): self.assertEqual(extract_experience("2 years, 4 years total"), 4)
