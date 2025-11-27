from pydantic import BaseModel, Field
from typing import List, Optional


class PRReviewRequest(BaseModel):
    owner: str = Field(..., description="GitHub repo owner/org name")
    repo: str = Field(..., description="GitHub repository name")
    pr_number: int = Field(..., description="Pull request number")
    github_token: str = Field(..., description="GitHub personal access token")


class DiffReviewRequest(BaseModel):
    diff: str = Field(..., description="Raw unified diff text")


class ReviewComment(BaseModel):
    file: str
    line: int
    issue: str
    severity: str
    suggestion: str


class ReviewResponse(BaseModel):
    summary: str
    comments: List[ReviewComment]
    raw_agent_output: Optional[dict] = Field(
        default=None,
        description="Optional debug info from intermediate agents"
    )
