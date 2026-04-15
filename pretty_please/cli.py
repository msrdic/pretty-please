"""Command-line interface for pretty-please."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pretty-please",
        description="Politely injects PLEASE into your LLM prompts.",
    )
    sub = parser.add_subparsers(dest="command")
    install_cmd = sub.add_parser("install-hook", help="Install the UserPromptSubmit hook")
    install_cmd.add_argument(
        "--codex", action="store_true", help="Install for Codex CLI (~/.codex/hooks.json) instead of Claude Code"
    )
    sub.add_parser("stats", help="Show prompt transformation stats")

    args = parser.parse_args()

    if args.command == "install-hook":
        if args.codex:
            from pretty_please.adapters.codex.install import install
        else:
            from pretty_please.adapters.claude_code.install import install
        install()
    elif args.command == "stats":
        from pretty_please.stats import show
        show()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
