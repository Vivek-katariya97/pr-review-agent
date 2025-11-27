import requests
from typing import List


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token

    def _headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[dict]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Returns the combined diff for all changed files in the PR.
        """
        files = self.get_pr_files(owner, repo, pr_number)
        diff_parts = []
        for f in files:
            filename = f.get("filename")
            patch = f.get("patch")
            if not patch:
                continue
            diff_parts.append(f"diff --git a/{filename} b/{filename}\n{patch}\n")
        return "\n".join(diff_parts)
