"""Gemini-powered learning path generation with safe, curated resources."""

import json
import os
from urllib.parse import quote_plus

from django.core.cache import cache

from skillgap.services import LEARNING_PATHS

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - exercised only when dependency is missing
    genai = None
    types = None


CACHE_SECONDS = 60 * 60 * 24
DEFAULT_MODEL = "gemini-3.7-flash"

# These are direct learning pages, not search-result pages. Keep the URLs
# controlled by the application instead of allowing the model to invent links.
RESOURCE_LINKS = {
    "python": ("GeeksforGeeks", "https://www.geeksforgeeks.org/python/python-programming-language/"),
    "html": ("GeeksforGeeks", "https://www.geeksforgeeks.org/html/html-tutorial/"),
    "css": ("GeeksforGeeks", "https://www.geeksforgeeks.org/css/css-tutorial/"),
    "javascript": ("GeeksforGeeks", "https://www.geeksforgeeks.org/javascript/javascript-tutorial/"),
    "django": ("GeeksforGeeks", "https://www.geeksforgeeks.org/python/django-tutorial/"),
    "sql": ("GeeksforGeeks", "https://www.geeksforgeeks.org/sql/sql-tutorial/"),
    "git": ("GeeksforGeeks", "https://www.geeksforgeeks.org/git/git-tutorial/"),
    "rest api": ("GeeksforGeeks", "https://www.geeksforgeeks.org/rest-api/"),
    "java": ("GeeksforGeeks", "https://www.geeksforgeeks.org/java/java/"),
    "oop": ("GeeksforGeeks", "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/"),
    "spring boot": ("GeeksforGeeks", "https://www.geeksforgeeks.org/springboot/spring-boot/"),
    "c++": ("GeeksforGeeks", "https://www.geeksforgeeks.org/cpp/cpp/"),
    "data structures": ("GeeksforGeeks", "https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/"),
    "algorithms": ("GeeksforGeeks", "https://www.geeksforgeeks.org/fundamentals-of-algorithms/"),
    "react": ("GeeksforGeeks", "https://www.geeksforgeeks.org/reactjs/reactjs-tutorials/"),
    "bootstrap": ("GeeksforGeeks", "https://www.geeksforgeeks.org/bootstrap/bootstrap-tutorial/"),
    "excel": ("GeeksforGeeks", "https://www.geeksforgeeks.org/excel/excel-tutorial/"),
    "pandas": ("GeeksforGeeks", "https://www.geeksforgeeks.org/pandas/pandas-tutorial/"),
    "numpy": ("GeeksforGeeks", "https://www.geeksforgeeks.org/python/numpy-tutorial/"),
    "matplotlib": ("GeeksforGeeks", "https://www.geeksforgeeks.org/python/matplotlib-tutorial/"),
    "power bi": ("GeeksforGeeks", "https://www.geeksforgeeks.org/power-bi/power-bi-tutorial/"),
    "machine learning": ("GeeksforGeeks", "https://www.geeksforgeeks.org/machine-learning/machine-learning/"),
    "statistics": ("GeeksforGeeks", "https://www.geeksforgeeks.org/statistics/statistics-tutorial/"),
    "scikit-learn": ("Scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html"),
    "tensorflow": ("TensorFlow Tutorials", "https://www.tensorflow.org/tutorials"),
}


def _resource_links(skill):
    """Return a direct curated resource plus a YouTube tutorial search."""
    clean_skill = str(skill).strip()
    key = clean_skill.lower()
    resource_name, resource_url = RESOURCE_LINKS.get(
        key,
        ("GeeksforGeeks", f"https://www.geeksforgeeks.org/?s={quote_plus(clean_skill)}"),
    )
    query = quote_plus(clean_skill)
    return {
        "resource_name": resource_name,
        "resource_url": resource_url,
        "youtube_url": f"https://www.youtube.com/results?search_query={query}+tutorial",
    }


def _fallback_path(missing_skills, job_role):
    path = []
    for index, skill in enumerate(missing_skills, start=1):
        resource = LEARNING_PATHS.get(
            skill,
            {
                "description": f"Learn the fundamentals of {skill} and practise it with a small project.",
                "level": "Beginner",
            },
        )
        path.append({
            "number": index,
            "skill": skill,
            "description": resource["description"],
            "level": resource["level"],
            **_resource_links(skill),
        })
    return path


def _normalise_items(items, missing_skills):
    allowed = {skill.lower(): skill for skill in missing_skills}
    result = []
    seen = set()

    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        raw_skill = str(item.get("skill", "")).strip()
        skill = allowed.get(raw_skill.lower())
        if not skill or skill.lower() in seen:
            continue
        seen.add(skill.lower())
        result.append({
            "number": len(result) + 1,
            "skill": skill,
            "description": str(item.get("description") or f"Learn the fundamentals of {skill}.").strip(),
            "level": str(item.get("level") or "Beginner").strip(),
            **_resource_links(skill),
        })

    # Never lose a missing skill if the model returns an incomplete response.
    existing = {item["skill"].lower() for item in result}
    for skill in missing_skills:
        if skill.lower() not in existing:
            fallback = _fallback_path([skill], "")[0]
            fallback["number"] = len(result) + 1
            result.append(fallback)
    return result


def generate_learning_path(job_role, missing_skills, current_skills=None):
    """Generate a personalised learning path, falling back to deterministic data."""
    missing_skills = [str(skill).strip() for skill in (missing_skills or []) if str(skill).strip()]
    current_skills = [str(skill).strip() for skill in (current_skills or []) if str(skill).strip()]

    if not missing_skills:
        return []

    cache_key = "ai-learning-path:" + str(abs(hash((job_role, tuple(sorted(missing_skills)), tuple(sorted(current_skills))))))
    cached = cache.get(cache_key)
    if cached:
        return cached

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or genai is None:
        path = _fallback_path(missing_skills, job_role)
        cache.set(cache_key, path, CACHE_SECONDS)
        return path

    prompt = f"""
You are a career-learning planner inside a college recruitment platform.
Create a practical learning path for a candidate targeting the job role: {job_role}.

Current skills:
{', '.join(current_skills) or 'Not provided'}

Required missing skills:
{', '.join(missing_skills)}

Return ONLY a JSON array. Create exactly one object for every missing skill and do not invent skills outside the supplied missing-skills list.
Each object must contain:
- skill: exact skill name from the supplied list
- description: 1-2 concise sentences explaining what to learn
- level: Beginner, Intermediate, or Advanced

Order the skills in a sensible prerequisite-to-advanced sequence.
Do not include URLs; the application supplies curated learning resources separately.
"""

    try:
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=1600,
            ),
        )
        items = json.loads(response.text or "[]")
        path = _normalise_items(items, missing_skills)
    except Exception:
        # AI failure must never prevent a candidate from seeing their ATS result.
        path = _fallback_path(missing_skills, job_role)

    cache.set(cache_key, path, CACHE_SECONDS)
    return path
