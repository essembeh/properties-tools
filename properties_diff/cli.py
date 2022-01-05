#!/bin/env python3

import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Dict

from colorama import Fore


def properties_to_dict(file: Path, separator="=", comment_char="#") -> Dict[str, str]:
    if not file.exists():
        raise FileExistsError(f"Cannot find file {file}")
    out = {}
    for lineno, line in enumerate(map(str.strip, file.read_text().splitlines())):
        if len(line) == 0:
            # empty line
            pass
        elif line.startswith(comment_char):
            # comment line
            pass
        elif separator not in line:
            # invalid line
            se = SyntaxError(
                f"Invalid file, no separator '{separator}' on line {lineno}"
            )
            se.lineno = lineno
            se.filename = str(file)
            se.text = line
            raise se
        else:
            index = line.index(separator)
            key = line[0:index].strip()
            value = line[index + len(separator) :].strip()
            if len(value) > 1 and value[0] == value[-1] == '"':
                value = value[1:-1]
            out[key] = value
    return out


def run(args=None):
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
        default="diff",
        help="select a format to show differences: using colors only (simple), using diff-like format (diff) or wdiff-like (wdiff) format. Default is 'diff'",
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

    args = parser.parse_args(args)

    def quote(data: dict, key: str):
        text = data.get(key, "")
        return f'"{text}"' if args.quote else text

    def date(file: Path):
        return datetime.isoformat(
            datetime.fromtimestamp(file.stat().st_mtime), timespec="seconds", sep=" "
        )

    try:
        left = properties_to_dict(args.left, separator=args.sep.strip())
        assert len(left) > 0, f"Cannot find any property in {args.left}"
        right = properties_to_dict(args.right, separator=args.sep.strip())
        assert len(right) > 0, f"Cannot find any property in {args.right}"

        added = [key for key in sorted(right) if key not in left]
        removed = [key for key in sorted(left) if key not in right]
        updated = [
            key for key in sorted(left) if key in right and left[key] != right[key]
        ]
        if len(added) == 0 and len(removed) == 0 and len(updated) == 0:
            print(f"Files {args.left} and {args.right} are similar")
        else:
            if not args.quiet:
                print(f"{Fore.YELLOW}--- {args.left}{Fore.RESET}    {date(args.left)}")
                print(
                    f"{Fore.YELLOW}+++ {args.right}{Fore.RESET}    {date(args.right)}"
                )

            if len(removed):
                print(f"{Fore.BLUE}# Only in {args.left}{Fore.RESET}")
                if args.mode == "simple":
                    for key in removed:
                        print(
                            f"{Fore.RED}{key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                elif args.mode == "diff":
                    for key in removed:
                        print(
                            f"{Fore.RED}- {key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                elif args.mode == "wdiff":
                    for key in removed:
                        print(
                            f"{Fore.RED}[-{key}{args.sep}{quote(left, key)}-]{Fore.RESET}"
                        )

            if len(added):
                print(f"{Fore.BLUE}# Only in {args.right}{Fore.RESET}")
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

            if len(updated):
                print(
                    f"{Fore.BLUE}# Updated from {args.left} to {args.right}{Fore.RESET}"
                )
                if args.mode == "simple":
                    for key in updated:
                        print(
                            f"{Fore.RED}{key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                    for key in updated:
                        print(
                            f"{Fore.GREEN}{key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "diff":
                    for key in updated:
                        print(
                            f"{Fore.RED}- {key}{args.sep}{quote(left, key)}{Fore.RESET}"
                        )
                        print(
                            f"{Fore.GREEN}+ {key}{args.sep}{quote(right, key)}{Fore.RESET}"
                        )
                elif args.mode == "wdiff":
                    for key in updated:
                        print(
                            f"{key}{args.sep}{Fore.RED}[-{quote(left, key)}-]{Fore.GREEN}{{+{quote(right, key)}+}}{Fore.RESET}"
                        )
    except BaseException as exc:
        print(f"{Fore.RED}ERROR: {exc}{Fore.RESET}", file=sys.stderr)
        if isinstance(exc, SyntaxError):
            print(f"{Fore.YELLOW}{exc.filename}:{exc.lineno}{Fore.RESET}  {exc.text}")
        sys.exit(1)
