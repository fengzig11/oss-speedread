"""把仓库元数据和 README 收成一份结构化速读结果。"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from speedread.parse import extract_how_to_run

SHANGHAI = timezone(timedelta(hours=8))

PERMISSIVE = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "0BSD",
    "Unlicense",
    "Zlib",
    "BSL-1.0",
}
COPYLEFT = {
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "GPL-2.0-only",
    "GPL-3.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-or-later",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
}
RESTRICTED = {"BUSL-1.1", "SSPL-1.0", "Commons-Clause", "Prosperity-3.0.0"}

AI_HINT = re.compile(
    r"\b(agent|llm|gpt|claude|gemini|mcp|rag|ontology|embedding|toolchain|"
    r"copilot|openai|anthropic|langchain|langgraph|skill|bot|multi-?agent)\b|"
    r"大模型|智能体|人工智能",
    re.I,
)
SECRET_HINT = re.compile(
    r"api[_ -]?key|secret[_ -]?key|access[_ -]?token|openai|anthropic|"
    r"gemini[_ -]?api|hf[_ -]?token|authorization:\s*bearer|\.env\b",
    re.I,
)
EXPERIMENTAL_HINT = re.compile(
    r"\b(not (?:for |production)|experimental|alpha\b|work in progress|\bwip\b|"
    r"prototype|research only|hackathon)\b|实验性|仅供研究|不可用于生产",
    re.I,
)
GPU_HINT = re.compile(r"\b(gpu|cuda|tpu|rocm)\b", re.I)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_shanghai(value: str | None) -> str:
    dt = parse_iso(value)
    if not dt:
        return "未知"
    local = dt.astimezone(SHANGHAI)
    days = max(0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days)
    if days == 0:
        rel = "今天"
    elif days == 1:
        rel = "1 天前"
    elif days < 30:
        rel = f"{days} 天前"
    elif days < 365:
        months = days // 30
        rel = f"约 {months} 个月前"
    else:
        years = days // 365
        rel = f"约 {years} 年前"
    return f"{local.strftime('%Y-%m-%d %H:%M')}（Asia/Shanghai），{rel}"


def days_since(value: str | None) -> int | None:
    dt = parse_iso(value)
    if not dt:
        return None
    return max(0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days)


def format_stars_cn(n: int) -> str:
    if n >= 10000:
        return f"{n / 10000:.1f} 万星"
    return f"{n:,} 星"


def license_info(meta: dict[str, Any]) -> dict[str, str]:
    lic = meta.get("license") or {}
    spdx = lic.get("spdx_id") or ""
    name = lic.get("name") or ""
    if not spdx or spdx == "NOASSERTION":
        return {
            "id": "未声明",
            "label": "未声明",
            "kind": "missing",
            "note": "仓库未声明开源许可，商用和再分发风险高。",
        }
    if spdx in PERMISSIVE:
        kind = "permissive"
        note = f"{spdx} 属于宽松许可，二次开发和商用相对省心（仍建议核对原文）。"
    elif spdx in COPYLEFT:
        kind = "copyleft"
        note = f"{spdx} 带 Copyleft，闭源商用或嵌入专有产品前要先看条款。"
    elif spdx in RESTRICTED or "source-available" in (name or "").lower():
        kind = "restricted"
        note = f"{spdx} 有额外限制，不能按普通开源来用。"
    else:
        kind = "other"
        note = f"许可为 {spdx}，使用前建议读一遍 LICENSE。"
    return {"id": spdx, "label": name or spdx, "kind": kind, "note": note}


def _blob_for_hints(meta: dict[str, Any], readme_text: str, root_files: list[str]) -> str:
    topics = meta.get("topics") or []
    parts = [
        meta.get("full_name") or "",
        meta.get("description") or "",
        " ".join(topics),
        " ".join(root_files),
        readme_text[:20000],
    ]
    return "\n".join(parts)


def display_name(meta: dict[str, Any]) -> str:
    full = meta.get("full_name") or ""
    name = meta.get("name") or (full.split("/")[-1] if full else "该项目")
    owner = full.split("/")[0] if "/" in full else ""
    pretty = name.replace("-", " ").title() if "-" in name else name
    if owner and owner.isupper() and owner.lower() not in pretty.lower():
        return f"{owner} {pretty}"
    return pretty


def _title_hook(meta: dict[str, Any]) -> str:
    desc = re.sub(r"\s+", " ", (meta.get("description") or "").strip())
    if not desc:
        return "本周值得一看的开源项目"
    desc = re.split(r"(?<=[。！？])\s+", desc)[0]
    # Keep a short first English sentence if it ends with .!?
    eng = re.split(r"(?<=[.!?])\s+", desc, maxsplit=1)[0]
    if eng and not re.search(r"[\u4e00-\u9fff]", eng):
        desc = eng
    cjk = bool(re.search(r"[\u4e00-\u9fff]", desc))
    limit = 36 if cjk else 80
    if len(desc) <= limit:
        return desc.rstrip(".")
    snippet = desc[:limit]
    if not cjk and " " in snippet:
        snippet = snippet.rsplit(" ", 1)[0]
    return snippet.rstrip(" ,;:，；：.。") + "…"


def _wechat_score(
    *,
    stars: int,
    days: int | None,
    how_found: bool,
    meta: dict[str, Any],
    readme_text: str,
    license_kind: str,
    latest_tag: str | None,
) -> dict[str, Any]:
    topics = [t.lower() for t in (meta.get("topics") or [])]
    blob = f"{meta.get('full_name','')} {meta.get('description','')} {' '.join(topics)} {readme_text[:4000]}"
    ai_related = bool(AI_HINT.search(blob))

    score = 1.0
    reasons: list[str] = []

    if stars >= 10000:
        score += 2.0
        reasons.append(f"热度高（{format_stars_cn(stars)}）")
    elif stars >= 3000:
        score += 1.5
        reasons.append(f"热度不错（{format_stars_cn(stars)}）")
    elif stars >= 1000:
        score += 1.0
        reasons.append(f"有一定热度（{format_stars_cn(stars)}）")
    elif stars >= 300:
        score += 0.5
        reasons.append("热度一般")
    else:
        reasons.append("星标不多，当资讯稿偏弱")

    if ai_related:
        score += 1.0
        reasons.append("和 Agent / 模型工具链相关，贴「风子开始读书」选题")
    else:
        reasons.append("和 AI 资讯号主线不够贴")

    if how_found:
        score += 0.5
        reasons.append("开源可跑的路径相对清楚")
    if license_kind != "missing":
        score += 0.2
    if latest_tag:
        score += 0.2
        reasons.append(f"有可引用的版本号（{latest_tag}）")

    if days is not None:
        if days <= 14:
            score += 0.5
            reasons.append("近期仍在更新，适合写时效稿")
        elif days > 180:
            score -= 0.5
            reasons.append("维护偏冷，当新闻稿不够新")

    final = int(max(1, min(5, round(score))))
    title = f"{display_name(meta)}：已有 {format_stars_cn(stars)}，{_title_hook(meta)}"
    return {
        "score": final,
        "reason": "；".join(reasons),
        "title_candidate": title,
        "ai_related": ai_related,
    }


def _build_risks(
    *,
    meta: dict[str, Any],
    license_data: dict[str, str],
    days: int | None,
    how_found: bool,
    readme_text: str,
    root_files: list[str],
    blob: str,
) -> list[str]:
    risks: list[str] = []
    risks.append(f"许可：{license_data['note']}")

    if meta.get("archived"):
        risks.append("仓库已归档（archived），上游不再活跃，不适合当长期依赖。")
    elif meta.get("disabled"):
        risks.append("仓库已被停用。")
    elif days is None:
        risks.append("维护活跃度：看不到最近推送时间。")
    elif days == 0:
        risks.append("维护活跃度：最近推送就在今天，目前看起来活跃。")
    elif days <= 14:
        risks.append(f"维护活跃度：最近推送在 {days} 天前，目前看起来活跃。")
    elif days <= 90:
        risks.append(f"维护活跃度：最近推送约在 {days} 天前，尚可。")
    elif days <= 180:
        risks.append(f"维护活跃度：最近推送约在 {days} 天前，节奏一般，跟进前先看 Issues。")
    else:
        risks.append(f"维护活跃度：最近推送约在 {days} 天前，可能已经停滞。")

    open_issues = meta.get("open_issues_count")
    stars_n = int(meta.get("stargazers_count") or 0)
    if isinstance(open_issues, int) and (
        open_issues >= 200
        or (open_issues >= 80 and open_issues / max(stars_n, 1) >= 0.03)
    ):
        risks.append(f"目前有 {open_issues} 个开放 Issue，社区负担不轻，踩坑成本可能偏高。")

    if any(name in {".env", ".env.example", ".env.sample", ".env.template"} for name in root_files):
        risks.append("根目录有环境变量样例（如 .env.example），运行前多半要自己配密钥。")
    elif SECRET_HINT.search(readme_text or ""):
        risks.append("README 提到 API Key / Token / .env，运行可能依赖第三方账号或付费模型。")

    if GPU_HINT.search(blob):
        risks.append("文档或描述里提到 GPU / CUDA，消费级电脑未必能完整跑起来。")

    if EXPERIMENTAL_HINT.search(blob):
        risks.append("项目自称实验性或未达生产级，更适合学习与 PoC，不要直接当线上依赖。")

    if not how_found:
        risks.append("生产可用性边界：连怎么跑都写不清，上手成本和踩坑概率都更高。")
    elif meta.get("archived"):
        pass
    else:
        risks.append("生产可用性边界：先当可演示的工具/PoC 来用；没看到明确的生产承诺前，不要默认它稳定。")

    # Deduplicate while preserving order
    unique: list[str] = []
    seen: set[str] = set()
    for item in risks:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


def _conclusion(
    *,
    meta: dict[str, Any],
    stars: int,
    days: int | None,
    how_found: bool,
    license_kind: str,
) -> str:
    if meta.get("archived"):
        return "不太建议当长期依赖：仓库已归档，资料可以看，但别押在它继续演进上。"
    if meta.get("disabled"):
        return "现在用不了：仓库已被停用。"

    score = 0.0
    if stars >= 5000:
        score += 2.0
    elif stars >= 1000:
        score += 1.2
    elif stars >= 200:
        score += 0.6

    if days is not None:
        if days <= 30:
            score += 2.0
        elif days <= 90:
            score += 1.0
        elif days <= 180:
            score += 0.4
        elif days > 365:
            score -= 1.5

    if how_found:
        score += 1.0
    if license_kind == "permissive":
        score += 0.4
    elif license_kind == "missing":
        score -= 1.0
    elif license_kind == "restricted":
        score -= 0.6

    name = meta.get("full_name") or "该仓库"
    if score >= 3.6:
        extra = "README 里能对上怎么跑，" if how_found else ""
        return f"能用，值得花时间：{extra}{format_stars_cn(stars)}，说明有人在用，最近也还在动。"
    if score >= 2.0:
        caveats = []
        if not how_found:
            caveats.append("安装步骤不够清楚")
        if license_kind == "missing":
            caveats.append("许可未声明")
        if days is not None and days > 180:
            caveats.append("维护偏冷")
        tail = f"（注意：{'、'.join(caveats)}）" if caveats else "，先当学习和演示，别急着上生产。"
        return f"可以上手试试{tail}"
    reasons = []
    if not how_found:
        reasons.append("README 没写清怎么跑")
    if days is not None and days > 180:
        reasons.append("更新偏少")
    if stars < 200:
        reasons.append("关注度不高")
    if license_kind == "missing":
        reasons.append("许可不明")
    detail = "，".join(reasons) or "信号偏弱"
    return f"可以扫一眼，眼下不值得投入太多时间：{name} {detail}。"


def analyze(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = bundle["meta"]
    readme_text = bundle.get("readme_text") or ""
    root_files = bundle.get("root_files") or []
    release = bundle.get("release")

    how = extract_how_to_run(readme_text)
    stars = int(meta.get("stargazers_count") or 0)
    forks = int(meta.get("forks_count") or 0)
    pushed_at = meta.get("pushed_at")
    days = days_since(pushed_at)
    license_data = license_info(meta)
    topics = meta.get("topics") or []
    latest_tag = None
    latest_release = None
    if isinstance(release, dict) and release.get("tag_name"):
        latest_tag = release.get("tag_name")
        latest_release = {
            "tag": release.get("tag_name"),
            "name": release.get("name"),
            "published_at": release.get("published_at"),
            "published_at_shanghai": format_shanghai(release.get("published_at")),
            "url": release.get("html_url"),
        }

    blob = _blob_for_hints(meta, readme_text, root_files)
    wechat = _wechat_score(
        stars=stars,
        days=days,
        how_found=bool(how.get("found")),
        meta=meta,
        readme_text=readme_text,
        license_kind=license_data["kind"],
        latest_tag=latest_tag,
    )
    risks = _build_risks(
        meta=meta,
        license_data=license_data,
        days=days,
        how_found=bool(how.get("found")),
        readme_text=readme_text,
        root_files=root_files,
        blob=blob,
    )
    conclusion = _conclusion(
        meta=meta,
        stars=stars,
        days=days,
        how_found=bool(how.get("found")),
        license_kind=license_data["kind"],
    )

    notable = [
        name
        for name in root_files
        if name.lower()
        in {
            "dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "go.mod",
            "cargo.toml",
            "makefile",
            "license",
            "license.md",
            ".env.example",
            "readme.md",
            "readme.rst",
        }
    ]

    return {
        "repo": meta.get("full_name"),
        "url": meta.get("html_url"),
        "description": meta.get("description") or "",
        "homepage": meta.get("homepage") or "",
        "archived": bool(meta.get("archived")),
        "conclusion": conclusion,
        "basics": {
            "stars": stars,
            "stars_label": format_stars_cn(stars),
            "forks": forks,
            "watchers": int(meta.get("subscribers_count") or 0),
            "open_issues": int(meta.get("open_issues_count") or 0),
            "license": license_data["id"],
            "license_label": license_data["label"],
            "pushed_at": pushed_at,
            "pushed_at_shanghai": format_shanghai(pushed_at),
            "created_at_shanghai": format_shanghai(meta.get("created_at")),
            "language": meta.get("language") or "未知",
            "topics": topics,
            "default_branch": meta.get("default_branch") or "unknown",
            "latest_release": latest_release,
            "root_files_notable": notable,
            "readme_name": bundle.get("readme_name"),
        },
        "how_to_run": how,
        "risks": risks,
        "wechat": wechat,
    }
