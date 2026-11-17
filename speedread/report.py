"""把分析结果渲染成中文 Markdown，或导出 JSON。"""

from __future__ import annotations

import json
from typing import Any


def render_markdown(result: dict[str, Any]) -> str:
    basics = result["basics"]
    how = result["how_to_run"]
    wechat = result["wechat"]
    topics = basics.get("topics") or []
    topics_text = "、".join(f"`{t}`" for t in topics) if topics else "无"

    lines: list[str] = [
        f"# 开源项目速读：{result.get('repo')}",
        "",
        f"- 仓库：{result.get('url')}",
    ]
    if result.get("description"):
        lines.append(f"- 简介：{result['description']}")
    if result.get("homepage"):
        lines.append(f"- 主页：{result['homepage']}")
    lines += [
        "",
        "## 1. 一句话结论",
        "",
        result.get("conclusion") or "暂无结论。",
        "",
        "## 2. 基本面",
        "",
        f"- Stars：{basics.get('stars_label')}（{basics.get('stars'):,}）",
        f"- Forks：{basics.get('forks'):,}",
        f"- License：{basics.get('license')}"
        + (f"（{basics.get('license_label')}）" if basics.get("license_label") and basics.get("license_label") != basics.get("license") else ""),
        f"- 最近推送：{basics.get('pushed_at_shanghai')}",
        f"- 主语言：{basics.get('language')}",
        f"- Topics：{topics_text}",
        f"- 默认分支：`{basics.get('default_branch')}`",
        f"- 创建时间：{basics.get('created_at_shanghai')}",
    ]
    if basics.get("watchers"):
        lines.append(f"- Watchers：{basics['watchers']:,}")
    if basics.get("open_issues") is not None:
        lines.append(f"- 开放 Issue：{basics['open_issues']:,}")

    latest = basics.get("latest_release")
    if latest:
        name = latest.get("name") or latest.get("tag")
        url = latest.get("url") or ""
        published = latest.get("published_at_shanghai") or ""
        extra = f"：[{name}]({url})" if url else f"：{name}"
        lines.append(f"- 最新 Release{extra}（{published}）")
    else:
        lines.append("- 最新 Release：暂无（或没有打过正式版）")

    notable = basics.get("root_files_notable") or []
    if notable:
        lines.append("- 根目录关键文件：" + "、".join(f"`{n}`" for n in notable))

    lines += ["", "## 3. 怎么跑", ""]
    if how.get("summary"):
        lines.append(str(how["summary"]))
        lines.append("")
    for section in how.get("sections") or []:
        title = section.get("title") or "未命名小节"
        body = (section.get("body") or "").strip()
        lines.append(f"### 摘自 README：{title}")
        lines.append("")
        lines.append(body)
        lines.append("")
    commands = how.get("commands") or []
    if commands:
        lines.append("关键命令（启发式抽取，请对照原 README）：")
        lines.append("")
        lines.append("```")
        lines.extend(commands)
        lines.append("```")
        lines.append("")

    lines += ["## 4. 风险点", ""]
    for item in result.get("risks") or []:
        lines.append(f"- {item}")
    if not result.get("risks"):
        lines.append("- 未识别到明显风险（仍建议自己读一遍 LICENSE 和 README）。")

    lines += [
        "",
        "## 5. 公众号素材分",
        "",
        f"**{wechat.get('score')}/5**（面向「风子开始读书」这类 AI 资讯号）",
        "",
        wechat.get("reason") or "",
        "",
        f"标题候选：{wechat.get('title_candidate')}",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_json(result: dict[str, Any]) -> str:
    payload = dict(result)
    payload["markdown"] = render_markdown(result)
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
