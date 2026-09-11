from unittest.mock import patch

from django.test import SimpleTestCase

from .ai_learning_path import generate_learning_path


class AILearningPathTests(SimpleTestCase):
    def test_fallback_returns_every_missing_skill_with_resources(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}, clear=False):
            result = generate_learning_path(
                "Python Developer",
                ["Django", "REST API"],
                current_skills=["Python"],
            )

        self.assertEqual([item["skill"] for item in result], ["Django", "REST API"])
        self.assertTrue(result[0]["youtube_url"].startswith("https://www.youtube.com/results"))
        self.assertTrue(result[0]["web_url"].startswith("https://www.google.com/search"))
        self.assertIn("description", result[0])
        self.assertIn("level", result[0])

    @patch("candidate.ai_learning_path.genai")
    def test_gemini_response_is_normalised_and_missing_skills_are_preserved(self, mock_genai):
        mock_client = mock_genai.Client.return_value
        mock_client.models.generate_content.return_value.text = (
            '[{"skill":"Pandas","description":"Learn dataframes and data cleaning.","level":"Intermediate"}]'
        )

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False):
            result = generate_learning_path(
                "Data Analyst",
                ["Pandas", "Power BI"],
                current_skills=["Python", "SQL"],
            )

        self.assertEqual([item["skill"] for item in result], ["Pandas", "Power BI"])
        self.assertEqual(result[0]["level"], "Intermediate")
        mock_client.models.generate_content.assert_called_once()
