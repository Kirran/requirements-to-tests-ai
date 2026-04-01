import re
from llm.prompts import SECTION_NAMES

def parse_ai_output(output_text):
    sections = {name: "" for name in SECTION_NAMES}
    current_section = None
    lines = output_text.splitlines()

    for line in lines:
        stripped = line.strip()

        matched_section = None
        for section in SECTION_NAMES:
            if stripped == section or stripped == f"{section}:":
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return {k: v.strip() for k, v in sections.items()}

def extract_risk_level(text):
    if not text:
        return None

    patterns = [
        r"Risk Level:\s*(Low|Medium|High)",
        r"Risk Level\s*\(\s*(Low|Medium|High)\s*\)",
        r"Overall Risk:\s*(Low|Medium|High)",
        r"Risk:\s*(Low|Medium|High)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).capitalize()

    return None

def extract_quality_score(text):
    if not text:
        return None

    match = re.search(r"(\d+)/10", text)
    if match:
        return int(match.group(1))
    return None  