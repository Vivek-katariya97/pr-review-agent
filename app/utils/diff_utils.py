def truncate_diff(diff: str, max_chars: int = 12000) -> str:
    """
    Simple safeguard: truncate very large diffs so the LLM doesn't explode.
    """
    if len(diff) <= max_chars:
        return diff
    return diff[:max_chars] + "\n\n... [truncated for analysis] ..."
