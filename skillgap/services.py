JOB_ROLE_SKILLS = {

    "Python Developer": [
        "Python",
        "Django",
        "SQL",
        "HTML",
        "CSS",
        "Git",
        "REST API",
    ],

    "Java Developer": [
        "Java",
        "OOP",
        "Spring Boot",
        "SQL",
        "HTML",
        "Git",
        "REST API",
    ],

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Python",
        "Django",
        "SQL",
        "Git",
        "REST API",
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Power BI",
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Machine Learning",
        "Statistics",
        "Scikit-learn",
    ],

    "Machine Learning Engineer": [
        "Python",
        "NumPy",
        "Pandas",
        "Machine Learning",
        "Scikit-learn",
        "TensorFlow",
        "SQL",
        "Git",
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "Bootstrap",
        "Python",
        "Django",
        "SQL",
        "Git",
    ],

    "Software Engineer": [
        "Python",
        "Java",
        "C++",
        "Data Structures",
        "Algorithms",
        "OOP",
        "SQL",
        "Git",
    ],
}


# Learning resources and order

LEARNING_PATHS = {

    "Python": {
        "description": "Learn Python programming fundamentals, functions, OOP and modules.",
        "level": "Beginner"
    },

    "HTML": {
        "description": "Learn HTML structure, forms, tables and semantic elements.",
        "level": "Beginner"
    },

    "CSS": {
        "description": "Learn CSS layouts, Flexbox, Grid, responsive design and styling.",
        "level": "Beginner"
    },

    "JavaScript": {
        "description": "Learn JavaScript fundamentals, DOM manipulation and events.",
        "level": "Intermediate"
    },

    "Django": {
        "description": "Learn Django project structure, models, forms, views and templates.",
        "level": "Intermediate"
    },

    "SQL": {
        "description": "Learn databases, SQL queries, joins, filtering and aggregation.",
        "level": "Beginner"
    },

    "Git": {
        "description": "Learn Git, GitHub, repositories, branching and version control.",
        "level": "Beginner"
    },

    "REST API": {
        "description": "Learn REST API concepts, HTTP methods, JSON and API integration.",
        "level": "Intermediate"
    },

    "Java": {
        "description": "Learn Java programming, classes, objects, collections and exceptions.",
        "level": "Beginner"
    },

    "OOP": {
        "description": "Learn object-oriented programming concepts such as inheritance and polymorphism.",
        "level": "Beginner"
    },

    "Spring Boot": {
        "description": "Learn Spring Boot, controllers, services, REST APIs and databases.",
        "level": "Intermediate"
    },

    "C++": {
        "description": "Learn C++ programming, OOP, STL and problem solving.",
        "level": "Intermediate"
    },

    "Data Structures": {
        "description": "Learn arrays, linked lists, stacks, queues, trees and graphs.",
        "level": "Intermediate"
    },

    "Algorithms": {
        "description": "Learn searching, sorting, recursion, greedy and dynamic programming.",
        "level": "Advanced"
    },

    "React": {
        "description": "Learn React components, props, state, hooks and routing.",
        "level": "Intermediate"
    },

    "Bootstrap": {
        "description": "Learn responsive layouts and UI components using Bootstrap.",
        "level": "Beginner"
    },

    "Excel": {
        "description": "Learn formulas, functions, charts, pivot tables and data cleaning.",
        "level": "Beginner"
    },

    "Pandas": {
        "description": "Learn data manipulation, cleaning and analysis using Pandas.",
        "level": "Intermediate"
    },

    "NumPy": {
        "description": "Learn numerical computing, arrays and mathematical operations.",
        "level": "Intermediate"
    },

    "Matplotlib": {
        "description": "Learn data visualization using charts and graphs.",
        "level": "Intermediate"
    },

    "Power BI": {
        "description": "Learn dashboards, data modeling and business intelligence.",
        "level": "Intermediate"
    },

    "Machine Learning": {
        "description": "Learn supervised learning, unsupervised learning and model evaluation.",
        "level": "Advanced"
    },

    "Statistics": {
        "description": "Learn probability, distributions, correlation and statistical analysis.",
        "level": "Intermediate"
    },

    "Scikit-learn": {
        "description": "Learn how to build and evaluate machine learning models with Scikit-learn.",
        "level": "Advanced"
    },

    "TensorFlow": {
        "description": "Learn neural networks and deep learning using TensorFlow.",
        "level": "Advanced"
    },
}


def analyze_skills(job_role, current_skills):

    required_skills = JOB_ROLE_SKILLS.get(job_role, [])

    # Convert user's input into a clean list
    user_skills = [
        skill.strip().lower()
        for skill in current_skills.split(",")
        if skill.strip()
    ]

    # Remove duplicate skills
    user_skills = list(dict.fromkeys(user_skills))

    required_lower = {
        skill.lower(): skill
        for skill in required_skills
    }

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill.lower() in user_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Calculate percentage
    if required_skills:
        match_percentage = round(
            (len(matched_skills) / len(required_skills)) * 100
        )
    else:
        match_percentage = 0

    # Create learning path
    learning_path = []

    for index, skill in enumerate(missing_skills, start=1):

        resource = LEARNING_PATHS.get(
            skill,
            {
                "description": f"Learn the fundamentals of {skill}.",
                "level": "Beginner"
            }
        )

        learning_path.append({
            "number": index,
            "skill": skill,
            "description": resource["description"],
            "level": resource["level"]
        })

    return {
        "job_role": job_role,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
        "learning_path": learning_path,
    }