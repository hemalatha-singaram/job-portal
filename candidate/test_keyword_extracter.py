from django.test import SimpleTestCase
from .keyword_extracter import extract_keywords, generate_tags
from .skill_matcher import match_skills, normalize_skill, split_skills


class KeywordMatcherTests(SimpleTestCase):
    def test_empty_keywords(self): self.assertEqual(extract_keywords(""), [])
    def test_stop_words_removed(self): self.assertNotIn("the", extract_keywords("the Python and Django"))
    def test_frequency_order(self): self.assertEqual(extract_keywords("Python Python Django")[0], "python")
    def test_keyword_limit(self): self.assertEqual(len(extract_keywords("alpha beta gamma delta", limit=2)), 2)
    def test_tags_are_unique_case_insensitively(self):
        tags = generate_tags(["Python"], ["python", "SQL"])
        self.assertEqual(sum(t.lower() == "python" for t in tags), 1)
    def test_normalize_skill(self): self.assertEqual(normalize_skill("React JS!"), "reactjs")
    def test_split_skills(self): self.assertEqual(split_skills("Python, SQL; Django|React"), ["Python", "SQL", "Django", "React"])
    def test_match_skills(self):
        matched, missing, score = match_skills(["Python", "SQL"], "Python, Django, SQL")
        self.assertEqual(matched, ["Python", "SQL"]); self.assertEqual(missing, ["Django"]); self.assertEqual(score, 66.67)
