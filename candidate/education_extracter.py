import re


def _near_heading(pattern, text, value_pattern, maximum, window=180):
    match = re.search(pattern, text, flags=re.I)
    if not match:
        return None
    segment = text[match.end(): match.end() + window]
    value = re.search(value_pattern, segment, flags=re.I | re.S)
    if not value:
        return None
    try:
        raw_number = next((group for group in value.groups() if group), value.group(1))
        number = float(raw_number)
        return number if 0 <= number <= maximum else None
    except ValueError:
        return None


def extract_education(text):
    if not text:
        return {}
    text = str(text)
    result = {}

    result["tenth_percentage"] = _near_heading(
        r"(?:10th|class\s*10|s\.?s\.?c|ssc)\b",
        text,
        r"(?:percentage|marks|score)?[^\d]{0,80}(\d{1,3}(?:\.\d{1,2})?)\s*%",
        100,
    )
    result["tenth_gpa"] = _near_heading(
        r"(?:10th|class\s*10|s\.?s\.?c|ssc)\b",
        text,
        r"(?:gpa|cgpa)\s*[:\-]?\s*(\d(?:\.\d{1,2})?)",
        10,
        window=120,
    )
    if result["tenth_gpa"] is None:
        result["tenth_gpa"] = _near_heading(
            r"(?:10th|class\s*10|s\.?s\.?c|ssc)\b",
            text,
            r"(\d{1,2}(?:\.\d{1,2})?)\s*(?:gpa|cgpa)",
            10,
            window=120,
        )
    result["intermediate_percentage"] = _near_heading(
        r"(?:intermediate|12th|class\s*12|hsc|higher\s*secondary)\b",
        text,
        r"(?:percentage|marks|score)?[^\d]{0,100}(\d{1,3}(?:\.\d{1,2})?)\s*%",
        100,
    )
    result["graduation_percentage"] = _near_heading(
        r"(?:b\.?tech|b\.?e\.?|bachelor(?:'s)?|graduation|degree)\b",
        text,
        r"(?:percentage|marks|score)?[^\d]{0,100}(\d{1,3}(?:\.\d{1,2})?)\s*%",
        100,
        window=100,
    )
    result["graduation_cgpa"] = _near_heading(
        r"(?:b\.?tech|b\.?e\.?|bachelor(?:'s)?|graduation|degree)\b",
        text,
        r"(?:cgpa|gpa)\s*[:\-]?\s*(\d(?:\.\d{1,2})?)",
        10,
        window=220,
    )
    return {key: value for key, value in result.items() if value is not None}
