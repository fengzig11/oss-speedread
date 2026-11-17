"""解析仓库地址，并从 README 里启发式抽取安装/启动步骤。"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from speedread.github import GitHubError

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
INSTALL_CMD_RE = re.compile(
    r"(?:^|\n)\s*(?:\$\s*)?((?:pip(?:3)?|uv|uvx|poetry|conda|npm|pnpm|yarn|bun|"
    r"cargo|go|brew|docker(?:-compose)?|make|git|curl|wget|python(?:3)?|npx|"
    r"composer|bundle|gem|pnpx)\s+[^\n]+)",
    re.IGNORECASE,
)

SECTION_WEIGHTS = [
    (re.compile(r"quick\s*start|getting\s*started|快速开始|快速上手|快速入门", re.I), 5),
    (re.compile(r"^install|^installation$|安装|部署", re.I), 5),
    (re.compile(r"how to (?:run|start|use)|running|启动|怎么跑|如何运行", re.I), 4),
    (re.compile(r"^setup$|usage|使用方法|使用说明", re.I), 3),
    (re.compile(r"example|demo|tutorial|示例|教程", re.I), 2),
]


def parse_repo_spec(spec: str) -> tuple[str, str]:
    raw = (spec or "").strip()
    if not raw:
        raise GitHubError("invalid_input", "请提供 GitHub 仓库地址，例如 owner/repo。")

    if raw.endswith(".git"):
        raw = raw[:-4]

    if raw.startswith("git@github.com:"):
        raw = raw[len("git@github.com:") :]

    if "github.com" in raw.lower():
        if "://" not in raw:
            raw = "https://" + raw
        parsed = urlparse(raw)
        host = (parsed.netloc or "").lower()
        if host not in {"github.com", "www.github.com"}:
            raise GitHubError("invalid_input", f"目前只支持 GitHub 仓库，收到的是：{host or raw}")
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) < 2:
            raise GitHubError("invalid_input", "无法从 URL 里解析出 owner/repo。")
        owner, repo = parts[0], parts[1]
    else:
        parts = [p for p in raw.strip("/").split("/") if p]
        if len(parts) != 2:
            raise GitHubError(
                "invalid_input",
                "仓库格式应为 owner/repo，或 https://github.com/owner/repo",
            )
        owner, repo = parts[0], parts[1]

    repo = repo.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        raise GitHubError("invalid_input", f"仓库名不合法：{owner}/{repo}")
    return owner, repo


def _heading_score(title: str) -> int:
    cleaned = title.strip().lstrip("#").strip()
    cleaned = re.sub(r"[^\w\s\u4e00-\u9fff/+-]", "", cleaned)
    best = 0
    for pattern, weight in SECTION_WEIGHTS:
        if pattern.search(cleaned):
            best = max(best, weight)
    return best


def _split_sections(markdown: str) -> list[tuple[int, str, str]]:
    """Return (level, title, body) sections. Leading text before first heading is level 0."""
    matches = list(HEADING_RE.finditer(markdown))
    if not matches:
        return [(0, "", markdown.strip())] if markdown.strip() else []

    sections: list[tuple[int, str, str]] = []
    preamble = markdown[: matches[0].start()].strip()
    if preamble:
        sections.append((0, "", preamble))

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        sections.append((len(match.group(1)), match.group(2).strip(), body))
    return sections


def _trim_block(text: str, max_chars: int = 1800) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].rsplit("\n", 1)[0].rstrip()
    return clipped + "\n\n…（后续已截断，完整步骤见原 README）"


def extract_how_to_run(readme_text: str) -> dict[str, object]:
    if not (readme_text or "").strip():
        return {
            "found": False,
            "summary": "README 未写清（仓库没有可读的 README）。",
            "sections": [],
            "commands": [],
        }

    sections = _split_sections(readme_text)
    scored: list[tuple[int, str, str]] = []
    for level, title, body in sections:
        if not title or not body:
            continue
        score = _heading_score(title)
        if score:
            scored.append((score, title, body))
    scored.sort(key=lambda item: item[0], reverse=True)

    picked: list[dict[str, str]] = []
    raw_bodies: list[str] = []
    seen_titles: set[str] = set()
    for score, title, body in scored:
        key = title.lower()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        raw_bodies.append(body)
        picked.append({"title": title, "body": _trim_block(body)})
        if len(picked) >= 2:
            break

    commands: list[str] = []
    search_space = "\n\n".join(raw_bodies) if raw_bodies else readme_text
    for match in INSTALL_CMD_RE.finditer(search_space):
        cmd = re.sub(r"\s+", " ", match.group(1)).strip().rstrip("\\").strip()
        if cmd.endswith(")") and cmd.count(")") > cmd.count("("):
            cmd = cmd[:-1].rstrip()
        if cmd and cmd not in commands:
            commands.append(cmd)
        if len(commands) >= 8:
            break

    if picked:
        return {
            "found": True,
            "summary": None,
            "sections": picked,
            "commands": commands,
        }

    if commands:
        return {
            "found": True,
            "summary": "README 没有独立的安装/快速开始小节，但从正文里扫到了这些命令：",
            "sections": [],
            "commands": commands,
        }

    return {
        "found": False,
        "summary": "README 未写清安装/启动步骤（未找到 Install / Quick Start / 安装 等段落，也没有明显的安装命令）。",
        "sections": [],
        "commands": [],
    }
