"""
diff cli tool entrypoint
"""

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional

from . import __version__
from .color import Color
from .utils import file_date, propertiesfile_to_dict


def run(argv: Optional[List[str]] = None):
    """
    diff cli
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
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
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color",
        action="store_const",
        dest="color",
        const=True,
        help="force colors",
    )
    color_group.add_argument(
        "--nocolor",
        action="store_const",
        dest="color",
        const=False,
        help="disable colors",
    )

    parser.add_argument(
        "--sep",
        default="=",
        help="key/value separator, default is '='",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-m",
        "--mode",
        choices=["simple", "diff", "wdiff"],
        default="wdiff",
        help="select a format to show differences: using colors only (simple), using diff-like format (diff) or wdiff-like (wdiff) format. Default is 'wdiff'",
    )
    mode_group.add_argument(
        "--diff",
        action="store_const",
        dest="mode",
        const="diff",
        help="use diff-like format to show differences",
    )
    mode_group.add_argument(
        "--wdiff",
        action="store_const",
        dest="mode",
        const="wdiff",
        help="use wdiff-like format to show differences",
    )
    mode_group.add_argument(
        "--simple",
        action="store_const",
        dest="mode",
        const="simple",
        help="use simple format to show differences",
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

    color = Color(args.color)

    def quote(data: dict, key: str):
        text = data.get(key, "")
        return f'"{text}"' if args.quote else text

    try:
        left = propertiesfile_to_dict(args.left, separator=args.sep)
        assert len(left) > 0, f"Cannot find any property in {args.left}"
        right = propertiesfile_to_dict(args.right, separator=args.sep)
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
                        color.yellow("***"),
                        color.yellow(args.left),
                        "(left)",
                        "  ",
                        file_date(args.left),
                    )
                    print(
                        color.yellow("***"),
                        color.yellow(args.right),
                        "(right)",
                        "  ",
                        file_date(args.right),
                    )
                else:
                    print(
                        color.yellow("---"),
                        color.yellow(args.left),
                        "(left)",
                        "  ",
                        file_date(args.left),
                    )
                    print(
                        color.yellow("+++"),
                        color.yellow(args.right),
                        "(right)",
                        "  ",
                        file_date(args.right),
                    )

            if len(deleted) and (args.sections is None or "deleted" in args.sections):
                print(color.blue(f"# Only in {args.left} (left)"))
                if args.mode == "simple":
                    for key in deleted:
                        print(color.red(f"{key}{args.sep}{quote(left, key)}"))
                elif args.mode == "diff":
                    for key in deleted:
                        print(color.red(f"- {key}{args.sep}{quote(left, key)}"))
                elif args.mode == "wdiff":
                    for key in deleted:
                        print(color.red(f"[-{key}{args.sep}{quote(left, key)}-]"))

            if len(added) and (args.sections is None or "added" in args.sections):
                print(color.blue(f"# Only in {args.right} (right)"))
                if args.mode == "simple":
                    for key in added:
                        print(color.green(f"{key}{args.sep}{quote(right, key)}"))
                elif args.mode == "diff":
                    for key in added:
                        print(color.green(f"+ {key}{args.sep}{quote(right, key)}"))
                elif args.mode == "wdiff":
                    for key in added:
                        print(color.green(f"{{+{key}{args.sep}{quote(right, key)}+}}"))

            if len(modified) and (args.sections is None or "updated" in args.sections):
                print(
                    color.blue(
                        f"# Updated from {args.left} (left) to {args.right} (right)"
                    )
                )
                if args.mode == "simple":
                    for key in modified:
                        print(color.red(f"{key}{args.sep}{quote(left, key)}"))
                    for key in modified:
                        print(color.green(f"{key}{args.sep}{quote(right, key)}"))
                elif args.mode == "diff":
                    for key in modified:
                        print(color.red(f"- {key}{args.sep}{quote(left, key)}"))
                        print(color.green(f"+ {key}{args.sep}{quote(right, key)}"))
                elif args.mode == "wdiff":
                    for key in modified:
                        print(
                            key,
                            args.sep,
                            color.red(f"[-{quote(left, key)}-]"),
                            color.green(f"{{+{quote(right, key)}+}}"),
                            sep="",
                        )
    except BaseException as exc:  # pylint: disable=broad-except
        print(color.red(f"ERROR: {exc}"), file=sys.stderr)
        if isinstance(exc, SyntaxError):
            print(
                color.yellow(f"[{exc.filename}:{exc.lineno}]"),
                "",
                exc.text,
                file=sys.stderr,
            )
        sys.exit(1)
