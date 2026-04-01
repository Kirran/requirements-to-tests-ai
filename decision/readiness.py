import re
from llm.parsing import (
    extract_quality_score,
    extract_risk_level,
)
def build_testing_readiness_decision(parsed_sections: dict) -> dict:
    quality_text = parsed_sections.get("Requirement Quality Score", "")
    gaps_text = parsed_sections.get("Requirement Gaps & Suggested Improvements", "")
    risk_text = parsed_sections.get("Engineering Risks", "")

    score = extract_quality_score(quality_text)
    risk_level = extract_risk_level(risk_text)
    confidence = extract_confidence_level(quality_text)

    gap_count = 0
    if gaps_text:
        gap_count = len([
            line for line in gaps_text.splitlines()
            if line.strip().startswith("-") or line.strip().startswith("•")
        ])
    
    if risk_level is None and score is not None:
        if score >= 8:
            risk_level = "Low"
        elif score >= 5:
            risk_level = "Medium"
        else:
            risk_level = "High"


    decision = "Needs Review"
    icon = "⚠️"
    summary = "The requirement needs additional review before reliable testing can begin."

    if score is None:
        return {
            "decision": decision,
            "icon": icon,
            "summary": summary,
            "score": None,
            "risk_level": risk_level,
            "confidence": confidence,
        }

    if risk_level is None and score is not None:
        if score >= 8:
            risk_level = "Low"
        elif score >= 5:
            risk_level = "Medium"
        else:
            risk_level = "High"

    if score >= 8 and risk_level == "Low" and gap_count <= 1:
        decision = "Ready for Testing"
        icon = "✅"
        summary = "The requirement appears sufficiently clear and testable for implementation and validation."
    elif score >= 6 and risk_level in {"Low", "Medium"} and gap_count <= 3:
        decision = "Testable with Minor Gaps"
        icon = "🟡"
        summary = "The requirement is mostly testable, but a few details should be clarified before execution."
    elif score >= 4:
        decision = "Requires Clarification"
        icon = "⚠️"
        summary = "The requirement is only partially testable because important details or edge cases are missing."
    else:
        decision = "Not Ready for Testing"
        icon = "⛔"
        summary = "The requirement is not test-ready and should be refined before formal test design begins."

    return {
        "decision": decision,
        "icon": icon,
        "summary": summary,
        "score": score,
        "risk_level": risk_level,
        "confidence": confidence,
    }

def extract_confidence_level(text: str) -> str | None:
    if not text:
        return None

    match = re.search(
        r"Confidence in Requirement Completeness:\s*(Low|Medium|High)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).capitalize()
    return None    