import re


def _number_after(patterns, text, maximum):
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            try:
                value = float(match.group(1))
                if 0 <= value <= maximum:
                    return value
            except ValueError:
                pass
    return None


def extract_education(text):
    if not text:
        return {}

    result = {}
    result["tenth_percentage"] = _number_after([
        r"(?:10th|class\s*10|ssc|secondary)\s*(?:exam|board)?\s*[:\-–|]?\s*(?:percentage|marks|score)?\s*[:\-–|]?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%?",
    ], text, 100)
    result["intermediate_percentage"] = _number_after([
        r"(?:intermediate|12th|class\s*12|hsc|higher\s*secondary)\s*(?:exam|board)?\s*[:\-–|]?\s*(?:percentage|marks|score)?\s*[:\-–|]?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%?",
    ], text, 100)
    result["graduation_percentage"] = _number_after([
        r"(?:b\.?tech|b\.?e\.?|bachelor(?:'s)?|graduation|degree)\s*[:\-–|]?[^\n]{0,45}?(?:percentage|marks|score)?\s*[:\-–|]?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%",
    ], text, 100)
    result["graduation_cgpa"] = _number_after([
        r"(?:b\.?tech|b\.?e\.?|bachelor(?:'s)?|graduation|degree)[^\n]{0,60}?(?:cgpa|gpa)\s*[:\-]?\s*(\d(?:\.\d{1,2})?)",
    ], text, 10)

    return {key: value for key, value in result.items() if value is not None}
