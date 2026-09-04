from django import template

from skillgap.services import LEARNING_PATHS

register = template.Library()


LEARNING_RESOURCES = {
    "Python": {"url": "https://docs.python.org/3/tutorial/", "source": "Python Official Tutorial"},
    "HTML": {"url": "https://developer.mozilla.org/en-US/docs/Web/HTML", "source": "MDN Web Docs"},
    "CSS": {"url": "https://developer.mozilla.org/en-US/docs/Web/CSS", "source": "MDN Web Docs"},
    "JavaScript": {"url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "source": "MDN Web Docs"},
    "Django": {"url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "source": "Django Official Tutorial"},
    "SQL": {"url": "https://www.w3schools.com/sql/", "source": "W3Schools SQL Tutorial"},
    "Git": {"url": "https://git-scm.com/docs/gittutorial", "source": "Git Official Tutorial"},
    "REST API": {"url": "https://developer.mozilla.org/en-US/docs/Glossary/REST", "source": "MDN Web Docs"},
    "Java": {"url": "https://dev.java/learn/", "source": "Java Official Learning"},
    "OOP": {"url": "https://docs.oracle.com/javase/tutorial/java/concepts/", "source": "Oracle Java Tutorial"},
    "Spring Boot": {"url": "https://spring.io/guides", "source": "Spring Official Guides"},
    "C++": {"url": "https://www.learncpp.com/", "source": "LearnCpp"},
    "Data Structures": {"url": "https://www.geeksforgeeks.org/data-structures/", "source": "GeeksforGeeks"},
    "Algorithms": {"url": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/", "source": "GeeksforGeeks"},
    "React": {"url": "https://react.dev/learn", "source": "React Official Learn"},
    "Bootstrap": {"url": "https://getbootstrap.com/docs/", "source": "Bootstrap Official Docs"},
    "Excel": {"url": "https://support.microsoft.com/en-us/excel", "source": "Microsoft Excel Support"},
    "Pandas": {"url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "source": "Pandas Official Tutorials"},
    "NumPy": {"url": "https://numpy.org/learn/", "source": "NumPy Official Learn"},
    "Matplotlib": {"url": "https://matplotlib.org/stable/tutorials/", "source": "Matplotlib Official Tutorials"},
    "Power BI": {"url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/", "source": "Microsoft Learn"},
    "Machine Learning": {"url": "https://developers.google.com/machine-learning/crash-course", "source": "Google Machine Learning Crash Course"},
    "Statistics": {"url": "https://www.khanacademy.org/math/statistics-probability", "source": "Khan Academy"},
    "Scikit-learn": {"url": "https://scikit-learn.org/stable/getting_started.html", "source": "Scikit-learn Official Guide"},
    "TensorFlow": {"url": "https://www.tensorflow.org/learn", "source": "TensorFlow Official Learn"},
}


@register.filter
def split_skills(value):
    if not value:
        return []
    return [item.strip() for item in str(value).replace(";", ",").replace("|", ",").split(",") if item.strip()]


@register.filter
def learning_resource(skill):
    """Return the learning description, level, and clickable source for a missing skill."""
    skill_text = str(skill or "").strip()
    for name, resource in LEARNING_PATHS.items():
        if name.lower() == skill_text.lower():
            result = dict(resource)
            result.update(LEARNING_RESOURCES.get(name, {}))
            return result
    result = {
        "description": f"Learn the fundamentals of {skill_text}.",
        "level": "Beginner",
    }
    result.update(LEARNING_RESOURCES.get(skill_text, {}))
    return result
