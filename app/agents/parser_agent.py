import json
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from .llm_client import get_llm


def run_parser_agent(diff_text: str) -> List[Dict[str, Any]]:
    """
    Uses an LLM to parse a unified diff into a structured representation.

    Output format (list of files):
    [
      {
        "file": "app/main.py",
        "changes": [
          {
            "type": "added" | "removed" | "modified",
            "line": 23,
            "content": "print('hello')"
          }
        ]
      }
    ]
    """
    llm = get_llm()

    # NOTE: We use double curly braces {{ }} to escape literal { } in LangChain templates.
    system_msg = (
        "You are a code diff parsing assistant. "
        "You will receive a unified code diff and must output a JSON array. "
        "Each element represents a single file with its changed lines.\n\n"
        "JSON schema:\n"
        "[\n"
        "  {{\n"
        '    "file": "path/to/file.py",\n'
        '    "changes": [\n'
        "      {{\n"
        '        "type": "added" | "removed" | "modified",\n'
        '        "line": <line_number_integer>,\n'
        '        "content": "line of code here"\n'
        "      }}\n"
        "    ]\n"
        "  }}\n"
        "]\n"
        "Only return valid JSON. Do not include backticks or comments."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("user", "Here is the diff:\n\n{diff_text}"),
        ]
    )

    chain = prompt | llm
    response = chain.invoke({"diff_text": diff_text})
    raw = response.content

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        else:
            return []
    except json.JSONDecodeError:
        # Fallback: if parsing fails, return empty or later handle gracefully
        return []
