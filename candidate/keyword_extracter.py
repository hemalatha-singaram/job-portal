import re
from collections import Counter


STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "from",
    "using", "used", "have", "has", "was", "were", "are",
    "will", "you", "your", "our", "their", "into", "about",
    "which", "where", "when", "while", "been", "being",
    "they", "them", "also", "than", "then", "these",
    "those", "such", "over", "under", "more", "most",
    "very", "can", "may", "not", "but", "all", "any",
    "job", "work", "working", "experience"
}


def extract_keywords(text, limit=20):

    if not text:
        return []

    words = re.findall(
        r'\b[a-zA-Z][a-zA-Z+#.-]{2,}\b',
        text.lower()
    )

    filtered_words = []

    for word in words:

        if word in STOP_WORDS:
            continue

        filtered_words.append(word)

    frequency = Counter(filtered_words)

    return [
        word
        for word, count in frequency.most_common(limit)
    ]


def generate_tags(skills, keywords):

    tags = []

    if skills:
        tags.extend(skills)

    if keywords:
        tags.extend(keywords[:10])

    unique_tags = []

    for tag in tags:
        if tag.lower() not in [
            existing.lower() for existing in unique_tags
        ]:
            unique_tags.append(tag)

    return unique_tags