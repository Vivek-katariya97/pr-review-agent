import json
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from .llm_client import get_llm


def run_reviewer_agent(parsed_changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Given parsed changes, uses LLM to produce code review comments.

    Expected output JSON:
    [
      {
        "file": "app/main.py",
        "line": 23,
        "issue": "Possible division by zero.",
        "severity": "high | medium | low",
        "suggestion": "Add a check to ensure denominator is not zero."
      }
    ]
    """
    if not parsed_changes:
        return []

    llm = get_llm()

    # Escape literal { } with {{ }} and }} in LangChain templates
    system_msg = (
        "You are a senior backend engineer performing code review on GitHub pull requests.\n"
        "You will receive a JSON structure describing code changes (by file and line).\n"
        "You must return a JSON array of code review comments.\n\n"
        "Focus on:\n"
        "- Logic / correctness\n"
        "- Performance\n"
        "- Security & injection risks\n"
        "- Readability & maintainability\n"
        "- API design & error handling\n\n"
        "Each review comment must follow this JSON schema:\n"
        "{{\n"
        '  "file": "path/to/file.py",\n'
        '  "line": <line_number_integer>,\n'
        '  "issue": "Short description of the problem.",\n'
        '  "severity": "high" | "medium" | "low",\n'
        '  "suggestion": "Concrete, actionable suggestion to fix or improve."\n'
        "}}\n\n"
        "Only return valid JSON (array). No backticks, no explanations."
    )

    user_msg = (
        "Here are the parsed code changes (JSON):\n\n"
        "{parsed_json}\n\n"
        "Generate the review comments."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("user", user_msg),
        ]
    )

    chain = prompt | llm
    response = chain.invoke({"parsed_json": json.dumps(parsed_changes, indent=2)})
    raw = response.content

    try:
        comments = json.loads(raw)
        if isinstance(comments, list):
            return comments
        return []
    except json.JSONDecodeError:
        return []
