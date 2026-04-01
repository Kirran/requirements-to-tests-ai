

def build_prompt(feature_type, combined_requirement):
    """Create the OpenAI prompt, customized by feature type."""

      # Extra guidance per feature type
    feature_type_guidance = {
        "UI Feature": """
        When the feature type is a UI Feature:
        - Emphasize usability, accessibility, and user flows.
        - Call out client-side and server-side validation.
        - Include cross-browser / cross-device behavior and layout edge cases.
        """,
        "API Endpoint": """
        When the feature type is an API Endpoint:
        - Focus on request/response contracts, status codes, and error handling.
        - Include tests for validation, authentication/authorization, rate limits, and idempotency.
        - Call out backward compatibility risks and versioning concerns if relevant.
        """,
        "Authentication Flow": """
        When the feature type is an Authentication Flow:
        - Prioritize security test cases (session handling, tokens, cookies, logout, MFA).
        - Include tests around password policies, reset flows, lockout, and brute-force protection.
        - Map risks to common OWASP categories where applicable.
        """,
        "File Upload": """
        When the feature type is a File Upload:
        - Emphasize file size/type limits, content validation, and malware scanning.
        - Include tests for partial uploads, timeouts, retries, and cleanup of temp files.
        - Cover storage, encryption, and access control for uploaded content.
        """,
        "Payment Flow": """
        When the feature type is a Payment Flow:
        - Focus on correctness of charges, refunds, and idempotency of payment requests.
        - Include tests for failures (network issues, declines, timeouts) and recovery behavior.
        - Call out security, compliance, and auditability (logging, reconciliation) considerations.
        """,
    }
    extra_instructions = feature_type_guidance.get(feature_type, "")
    
    return f"""
    You are a senior QA Architect focused on shift-left quality engineering.

    Analyze the requirement below and produce structured QA analysis.

    Feature Type:
    {feature_type}

    Requirement Context:
    {combined_requirement}

    Return the results using these exact section headers in this exact order:
    Write the headers exactly as shown and start each section on a new line.

    Requirement Quality Assessment:
    Requirement Summary:
    Requirement Gaps & Suggested Improvements:
    Engineering Risks:
    Test Strategy Summary:
    Functional Test Cases:
    Negative Test Cases:
    Edge Cases:
    Security Test Cases:
    Root Cause Signals:
    Observability / Logging Recommendations:
    Requirement Quality Score:
    Additional guidance for this feature type:
        {extra_instructions}

    Rules:
    - Use each section header exactly as written above.
    - Under each section, use bullet points.
    - Keep responses concise and practical.
    - Do not repeat the same issue across multiple sections.
    - Each section should contain unique insights.
    - Focus on real engineering risks and missing requirement details.
    - Do not add any introduction or conclusion outside these sections.
    - Do not modify, rename, or reorder the section titles.
    - Use the exact phrase "Risk Level: <Low|Medium|High>" in the Engineering Risks section.
    - Do not use parentheses or alternate wording for the risk level.

    For the Engineering Risks section:
    - The first bullet must use the exact format: Risk Level: Low / Medium / High
    - Then provide the key engineering and product risks.
    - Do not use parentheses or alternate wording for the risk level.
    
    For the Test Strategy Summary section:
    - Provide 3 to 5 concise bullets.
    - Summarize the overall testing approach for this requirement.
    - Focus on priority test areas, test depth, and major validation categories.
    - Do not repeat detailed test cases verbatim.
    - Make it useful for a QA lead, engineer, or product manager planning validation work.

    For the Requirement Quality Score section:
    - Include a bullet in the exact format: Requirement Quality Score: X/10
    - Include a bullet in the exact format: Confidence in Requirement Completeness: Low / Medium / High
    - Briefly explain why this score was assigned.

    For the Requirement Gaps & Suggested Improvements section:
    - Provide 3 to 5 bullets.
    - Each bullet must contain two parts:
    - Gap: describe what is missing or unclear in the requirement.
    - Fix: describe a concrete action to improve clarity or testability.
    - Keep the wording concise and practical.
    - Do not repeat the same idea in multiple bullets.
    - Make each fix specific and implementation-friendly.

    """.strip()
