"""GitHub 公开 API 客户端。优先用环境变量或 gh 的 token，没有也能读公开仓。"""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
from typing import Any

import requests

API = "https://api.github.com"
USER_AGENT = "oss-speedread/0.1"


class GitHubError(Exception):
    def __init__(self, kind: str, message: str, status: int | None = None):
        super().__init__(message)
        self.kind = kind
        self.message = message
        self.status = status


def _token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value.strip()
    if shutil.which("gh"):
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            token = (result.stdout or "").strip()
            if result.returncode == 0 and token:
                return token
        except (OSError, subprocess.SubprocessError):
            return None
    return None


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(path: str, *, allow_404: bool = False) -> Any | None:
    url = f"{API}{path}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=20)
    except requests.RequestException as exc:
        raise GitHubError("network", f"网络请求失败：{exc}") from exc

    if resp.status_code == 404:
        if allow_404:
            return None
        raise GitHubError("not_found", "仓库不存在，或者未公开（404）。", 404)

    if resp.status_code in (403, 429):
        payload_msg = ""
        try:
            payload_msg = str(resp.json().get("message") or "")
        except ValueError:
            payload_msg = (resp.text or "")[:240]
        remaining = resp.headers.get("X-RateLimit-Remaining")
        rate_limited = (
            resp.status_code == 429
            or remaining == "0"
            or "rate limit" in payload_msg.lower()
        )
        if rate_limited:
            extra = "可设置环境变量 GITHUB_TOKEN（或先 gh auth login）提高限额。"
            raise GitHubError(
                "rate_limit",
                f"GitHub API 频率受限。{extra}",
                resp.status_code,
            )
        raise GitHubError(
            "forbidden",
            f"GitHub API 拒绝请求（{resp.status_code}）：{payload_msg or '无详细信息'}",
            resp.status_code,
        )

    if resp.status_code >= 400:
        payload_msg = ""
        try:
            payload_msg = str(resp.json().get("message") or "")
        except ValueError:
            payload_msg = (resp.text or "")[:240]
        raise GitHubError(
            "api_error",
            f"GitHub API 出错（{resp.status_code}）：{payload_msg or '无详细信息'}",
            resp.status_code,
        )

    try:
        return resp.json()
    except ValueError as exc:
        raise GitHubError("api_error", "GitHub API 返回了无法解析的内容。") from exc


def decode_readme(payload: dict[str, Any]) -> str:
    content = payload.get("content") or ""
    encoding = payload.get("encoding") or ""
    if encoding == "base64":
        raw = base64.b64decode(content)
        return raw.decode("utf-8", errors="replace")
    if isinstance(content, str):
        return content
    return ""


def fetch_repo_bundle(owner: str, repo: str) -> dict[str, Any]:
    meta = api_get(f"/repos/{owner}/{repo}")
    readme_payload = api_get(f"/repos/{owner}/{repo}/readme", allow_404=True)
    release = api_get(f"/repos/{owner}/{repo}/releases/latest", allow_404=True)
    root = api_get(f"/repos/{owner}/{repo}/contents/", allow_404=True)

    readme_text = ""
    readme_name = None
    if isinstance(readme_payload, dict):
        readme_text = decode_readme(readme_payload)
        readme_name = readme_payload.get("name")

    root_files: list[str] = []
    if isinstance(root, list):
        root_files = [item.get("name", "") for item in root if item.get("name")]

    return {
        "meta": meta,
        "readme_text": readme_text,
        "readme_name": readme_name,
        "release": release if isinstance(release, dict) else None,
        "root_files": root_files,
    }
