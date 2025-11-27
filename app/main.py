from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.review_models import (
    PRReviewRequest,
    DiffReviewRequest,
    ReviewResponse,
    ReviewComment,
)
from app.services.github_service import GitHubService
from app.utils.diff_utils import truncate_diff
from app.agents.parser_agent import run_parser_agent
from app.agents.reviewer_agent import run_reviewer_agent
from app.agents.summary_agent import run_summary_agent


app = FastAPI(
    title="Automated GitHub PR Review Agent",
    description="FastAPI + LangChain multi-agent backend for PR review",
    version="0.1.0",
)

# Simple CORS config (you can tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/review/pr", response_model=ReviewResponse)
async def review_pr(request: PRReviewRequest):
    """
    Review a GitHub PR by fetching its diff and passing through multi-agent pipeline.
    """
    try:
        gh = GitHubService(token=request.github_token)
        diff = gh.get_pr_diff(request.owner, request.repo, request.pr_number)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub error: {e}")

    if not diff:
        raise HTTPException(status_code=400, detail="No diff content found for this PR.")

    truncated_diff = truncate_diff(diff)

    # Agent 1: Parse diff
    parsed_changes = run_parser_agent(truncated_diff)

    # Agent 2: Generate review comments
    raw_comments = run_reviewer_agent(parsed_changes)

    # Map raw agent output into Pydantic ReviewComment models
    comments = []
    for c in raw_comments:
        try:
            comments.append(
                ReviewComment(
                    file=c.get("file", ""),
                    line=int(c.get("line", 0)),
                    issue=c.get("issue", ""),
                    severity=c.get("severity", "medium"),
                    suggestion=c.get("suggestion", ""),
                )
            )
        except Exception:
            # Skip malformed comments
            continue

    # Agent 3: Summarize
    summary = run_summary_agent([c.model_dump() for c in comments])

    return ReviewResponse(
        summary=summary,
        comments=comments,
        raw_agent_output={
            "parsed_changes": parsed_changes,
            "raw_comments": raw_comments,
        },
    )


@app.post("/review/diff", response_model=ReviewResponse)
async def review_diff(request: DiffReviewRequest):
    """
    Review a manually provided diff (no GitHub integration).
    """
    if not request.diff.strip():
        raise HTTPException(status_code=400, detail="Diff must not be empty.")

    truncated_diff = truncate_diff(request.diff)

    # Agent 1: Parse diff
    parsed_changes = run_parser_agent(truncated_diff)

    # Agent 2: Generate review comments
    raw_comments = run_reviewer_agent(parsed_changes)

    comments = []
    for c in raw_comments:
        try:
            comments.append(
                ReviewComment(
                    file=c.get("file", ""),
                    line=int(c.get("line", 0)),
                    issue=c.get("issue", ""),
                    severity=c.get("severity", "medium"),
                    suggestion=c.get("suggestion", ""),
                )
            )
        except Exception:
            continue

    # Agent 3: Summarize
    summary = run_summary_agent([c.model_dump() for c in comments])

    return ReviewResponse(
        summary=summary,
        comments=comments,
        raw_agent_output={
            "parsed_changes": parsed_changes,
            "raw_comments": raw_comments,
        },
    )
