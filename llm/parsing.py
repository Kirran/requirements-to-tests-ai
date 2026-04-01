import re
from llm.schema import SECTION_SCHEMA
import streamlit as st



def parse_ai_output(output_text):
    sections = {key: "" for key in SECTION_SCHEMA.keys()}
    current_key = None

    for line in output_text.splitlines():
        stripped = line.strip()

        # normalize heading line
        normalized = stripped.lstrip("#").strip()
        normalized = normalized.strip("*").strip()
        normalized = normalized.rstrip(":").strip()

        matched_key = None
        for key, label in SECTION_SCHEMA.items():
            if normalized == label:
                matched_key = key
                break

        if matched_key:
            current_key = matched_key
            continue

        if current_key:
            sections[current_key] += line + "\n"

    parsed_sections = {k: v.strip() for k, v in sections.items()}
    
    return parsed_sections

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