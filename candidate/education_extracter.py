import re


def extract_education(text):
    """Best-effort extraction of common percentage/CGPA education values."""
    result = {}
    if not text:
        return result

    patterns = {
        'tenth_percentage': r'(?:10th|ssc|secondary)[^\n%]{0,60}(\d{1,3}(?:\.\d{1,2})?)\s*%',
        'intermediate_percentage': r'(?:intermediate|12th|hsc|higher secondary)[^\n%]{0,60}(\d{1,3}(?:\.\d{1,2})?)\s*%',
        'graduation_percentage': r'(?:b\.?tech|b\.?e\.?|bachelor|graduation|degree)[^\n%]{0,80}(\d{1,3}(?:\.\d{1,2})?)\s*%',
        'graduation_cgpa': r'(?:b\.?tech|b\.?e\.?|bachelor|graduation|degree)[^\n]{0,80}(?:cgpa|gpa)[^\d]{0,10}(\d(?:\.\d{1,2})?)',
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if match:
            try:
                result[field] = float(match.group(1))
            except ValueError:
                pass

    return result
