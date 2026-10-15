import re

BOARD_NAMES = [
    "CBSE",
    "ICSE",
    "CISCE",
    "State Board",
    "Karnataka State Board",
    "NIOS",
]

PATTERNS = {
    "Date": [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b",
    ],
    "Circular": [r"\bNo\.?\s*[\w/-]+/\d{4}\b"],
    "Quantity": [r"\b\d+\s*(?:seats|marks|years)\b"],
    "Rule": [r"\bRule\s+\d+\b"],
}


def gazetteer_pattern(names):
    names = sorted(set(n.strip() for n in names if n and n.strip()), key=len, reverse=True)
    if not names:
        return None
    alternatives = "|".join(re.escape(name) for name in names)
    return re.compile(r"(?<!\w)(?:" + alternatives + r")(?!\w)", re.IGNORECASE)


def extract_entities(text, schools=None, roads=None, localities=None):
    spans = []

    gazetteers = {
        "School": schools or [],
        "Road": roads or [],
        "Locality": localities or [],
        "Board": BOARD_NAMES,
    }

    for entity_type, names in gazetteers.items():
        pattern = gazetteer_pattern(names)
        if pattern:
            for match in pattern.finditer(text):
                spans.append((entity_type, match.start(), match.end(), match.group()))

    for entity_type, patterns in PATTERNS.items():
        for regex in patterns:
            for match in re.finditer(regex, text, re.IGNORECASE):
                spans.append((entity_type, match.start(), match.end(), match.group()))

    return sorted(set(spans), key=lambda item: (item[1], item[2], item[0]))
