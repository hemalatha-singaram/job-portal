import re


def extract_experience(text):
    """Return explicit professional experience in whole years.

    Internship durations are intentionally not counted as full-time experience
    unless the resume explicitly states a number of years of experience.
    """
    if not text:
        return 0
    years = [float(v) for v in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", str(text), re.I)]
    return int(max(years)) if years else 0
