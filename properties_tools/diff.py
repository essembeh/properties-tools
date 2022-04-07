"""
diff cli tool entrypoint
"""

import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from colorama import Fore

from .utils import properties_to_dict


def run(argv: Optional[List[str]] = None):
    """
    diff cli
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="print less information",
    )
    parser.add_argument(
        "--quote",
        action="store_true",
        help='use double quotes for values, example: foo="bar"',
    )
    parser.add_argument(
        "--sep",
        default="=",
        help="key/value separator, default is '='",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["simple", "diff", "wdiff"],
        default="wdiff",
        help="select a format to show differences: using colors only (simple), using diff-like format (diff) or wdiff-like (wdiff) format. Default is 'wdiff'",
    )
    parser.add_argument(
        "-A",
        "--added",
        action="append_const",
        dest="sections",
        const="added",
        help="print added properties",
    )
    parser.add_argument(
        "-D",
        "--deleted",
        action="append_const",
        dest="sections",
        const="deleted",
        help="print deleted properties",
    )
    parser.add_argument(
        "-U",
        "--updated",
        action="append_const",
        dest="sections",
        const="updated",
        help="print updated properties",
    )
    parser.add_argument(
        "left",
        type=Path,
        metavar="left.properties",
        help="left file to compare",
    )
    parser.add_argument(
        "right",
        type=Path,
        metavar="right.properties",
        help="right file to compare",
    )

    args = parser.parse_args(argv)

    def quote(data: dict, key: str):
        text = data.get(key, "")
        return f'"{text}"' if args.quote else text

    def date(file: Path):
        return datetime.isoformat(
            datetime.fromtimestamp(file.stat().st_mtime), timespec="seconds", sep=" "
        )

    try:
        left = properties_to_dict(args.left, separator=args.sep)
        assert len(left) > 0, f"Cannot find any property in {args.left}"
        right = properties_to_dict(args.right, separator=args.sep)
        assert len(right) > 0, f"Cannot find any property in {args.right}"

        added = [key for key in sorted(right) if key not in left]
        deleted = [key for key in sorted(left) if key not in right]
        modified = [
            key for key in sorted(left) if key in right and left[key] != right[key]
        ]
        if len(added) == 0 and len(deleted) == 0 and len(modified) == 0:
            print(f"Files {args.left} and {args.right} are similar")
        else:
            if not args.quiet:
                if args.mode == "simple":
                    print(
                        f"{Fore.YELLOW}*** {args.left}{Fore.RESET} (left)    {date(args.left)}"
                    )
                    print(
                        f"{Fore.YELLOW}*** {args.right}{Fore.RESET} (right)    {date(args.right)}"
                    )
                else:
                    print(
                        f"{Fore.YELLOW}--- {args.left}{Fore.RESET} (left)    {date(args.left)}"
                    )
                    print(
                        f"{Fore.YELLOW}+++ {args.right}{Fore.RESET} (right)    {date(args.right)}"
                    )

            if len(deleted) and (args.sections is None or "deleted" in args.sections):
                print(f"{Fore.BLUE}# Only in {args.left} (left){Fore.RESET}")
                if args.mode == "simple":
                    for key in deleted:
                        print(
                            f"{Fore.RED}{key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                elif args.mode == "diff":
                    for key in deleted:
                        print(
                            f"{Fore.RED}- {key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                elif args.mode == "wdiff":
                    for key in deleted:
                        print(
                            f"{Fore.RED}[-{key}{args.sep}{quote(left, key)}-]{Fore.RESET}"
                        )

            if len(added) and (args.sections is None or "added" in args.sections):
                print(f"{Fore.BLUE}# Only in {args.right} (right){Fore.RESET}")
                if args.mode == "simple":
                    for key in added:
                        print(
                            f"{Fore.GREEN}{key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "diff":
                    for key in added:
                        print(
                            f"{Fore.GREEN}+ {key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "wdiff":
                    for key in added:
                        print(
                            f"{Fore.GREEN}{{+{key}{args.sep}{quote(right, key)}+}}{Fore.RESET}"
                        )

            if len(modified) and (args.sections is None or "updated" in args.sections):
                print(
                    f"{Fore.BLUE}# Updated from {args.left} (left) to {args.right} (right){Fore.RESET}"
                )
                if args.mode == "simple":
                    for key in modified:
                        print(
                            f"{Fore.RED}{key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                    for key in modified:
                        print(
                            f"{Fore.GREEN}{key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "diff":
                    for key in modified:
                        print(
                            f"{Fore.RED}- {key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                        print(
                            f"{Fore.GREEN}+ {key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "wdiff":
                    for key in modified:
                        print(
                            f"{key}{args.sep}{Fore.RED}[-{quote(left, key)}-]{Fore.GREEN}{{+{quote(right, key)}+}}{Fore.RESET}"
                        )
    except BaseException as exc:
        print(f"{Fore.RED}ERROR: {exc}{Fore.RESET}", file=sys.stderr)
        if isinstance(exc, SyntaxError):
            print(
                f"{Fore.YELLOW}{exc.filename}:{exc.lineno}{Fore.RESET}  {exc.text}",
                file=sys.stderr,
            )
        sys.exit(1)
