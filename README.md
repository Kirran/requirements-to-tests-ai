# Specs-to-Tests — AI Requirement Analysis Assistant

Specs-to-Tests is a prototype tool that explores how AI can help improve requirement quality and support shift-left testing practices.

The application analyzes software requirements from Jira tickets or manual input and generates structured insights including requirement gaps, risk signals, and test strategy recommendations.

The goal is to help product managers, developers, and quality engineers identify incomplete or risky requirements earlier in the development lifecycle.

---

## Features

- Analyze Jira tickets using the Jira REST API
- Accept manual or voice input for additional requirement context
- AI-assisted requirement analysis using OpenAI models
- Generate structured insights, including:
  - Requirement gaps
  - Risk signals
  - Functional and negative test cases
  - Edge cases and security considerations
  - Root cause signals
  - Observability and logging recommendations
- Requirement readiness scoring
- Export analysis as Markdown for documentation

---

## Architecture

The application combines several components:

- **Streamlit UI** for interactive requirement analysis
- **Jira REST API** to retrieve requirement details
- **OpenAI API** to generate structured QA insights
- **Python parsing layer** to convert AI output into structured sections

Workflow:
