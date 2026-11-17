"""命令行入口：python -m speedread <owner/repo 或 GitHub URL>"""

from __future__ import annotations

import argparse
import sys

from speedread import __version__
from speedread.analyze import analyze
from speedread.github import GitHubError, fetch_repo_bundle
from speedread.parse import parse_repo_spec
from speedread.report import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="speedread",
        description="开源项目速读助手：输入 GitHub 仓库，输出一页中文报告。",
    )
    parser.add_argument(
        "repo",
        help="仓库地址，例如 NVIDIA/auto-ontology 或 https://github.com/NVIDIA/auto-ontology",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出结构化 JSON（内含 markdown 字段）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"oss-speedread {__version__}",
    )
    return parser


def run(repo_spec: str, as_json: bool = False) -> str:
    owner, name = parse_repo_spec(repo_spec)
    bundle = fetch_repo_bundle(owner, name)
    result = analyze(bundle)
    return render_json(result) if as_json else render_markdown(result)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = run(args.repo, as_json=args.json)
    except GitHubError as exc:
        print(f"速读失败：{exc.message}", file=sys.stderr)
        if exc.kind == "invalid_input":
            return 2
        if exc.kind == "not_found":
            return 3
        if exc.kind == "rate_limit":
            return 4
        return 1
    except KeyboardInterrupt:
        print("已取消。", file=sys.stderr)
        return 130
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
