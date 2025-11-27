import json
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from .llm_client import get_llm


def run_summary_agent(review_comments: List[Dict[str, Any]]) -> str:
    """
    Summarize the review comments into a short, clear PR summary.
    """
    if not review_comments:
        return "No major issues found in the changed code. The PR looks good overall."

    llm = get_llm(temperature=0.3)

    system_msg = (
        "You are a helpful senior engineer writing a pull request review summary.\n"
        "Given a list of review comments (as JSON), write a concise summary for the PR description.\n"
        "Highlight critical issues first, then mention medium/low severity suggestions."
    )

    user_msg = (
        "Here are the review comments as JSON:\n\n"
        "{comments_json}\n\n"
        "Write a short summary (3–6 sentences)."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            ("user", user_msg),
        ]
    )

    chain = prompt | llm
    response = chain.invoke({"comments_json": json.dumps(review_comments, indent=2)})
    return response.content.strip()
