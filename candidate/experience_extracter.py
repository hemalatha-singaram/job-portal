import re


def extract_experience(text):
    """
    Extract total years of experience from resume text.
    Returns experience as a whole number.
    """

    if not text:
        return 0

    text_lower = text.lower()

    years = []

    # Find patterns such as:
    # 1 year
    # 2 years
    # 3+ years
    year_matches = re.findall(
        r'(\d+(?:\.\d+)?)\s*\+?\s*years?',
        text_lower
    )

    for value in year_matches:
        years.append(float(value))

    # Find patterns such as:
    # 6 months
    # 12 months
    month_matches = re.findall(
        r'(\d+)\s*months?',
        text_lower
    )

    months = []

    for value in month_matches:
        months.append(int(value))

    # If years were found, use the highest value
    if years:
        return int(max(years))

    # If only months were found
    if months:
        return int(max(months) / 12)

    # No experience information found
    return 0