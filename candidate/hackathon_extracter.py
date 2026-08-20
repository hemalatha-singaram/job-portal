import re

HEADING = re.compile(r"^\s*(?:hackathons?|hackathon experience)\s*(?:[:\-–—])?\s*$", re.I)
STOP = re.compile(r"^\s*(?:education|skills|technical skills|certifications?|certificates?|references|languages|projects?|experience|internships?)\s*(?:[:\-–—])?\s*$", re.I)


def extract_hackathons(text):
    if not text:
        return ""
    lines = [line.strip(" /|") for line in str(text).replace("\r", "\n").replace("\t", "\n").splitlines()]
    for i, line in enumerate(lines):
        if HEADING.match(line):
            collected = []
            for candidate in lines[i + 1:]:
                if STOP.match(candidate):
                    break
                if candidate:
                    collected.append(candidate)
            return "\n".join(collected).strip()
    return ""
