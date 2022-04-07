"""
diff cli tool entrypoint
"""

import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from colorama import Fore, Style
from colorama.ansi import Cursor, clear_line

from .utils import parse_line, properties_to_dict, syntax_error


def run(argv: Optional[List[str]] = None):
    """
    patch cli
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        help="print colors",
    )
    parser.add_argument(
        "--comments",
        dest="comments",
        action="store_true",
        help="insert comment when property is added, updated or deleted",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force output file (--output) overwrite if it already exists",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="ask for confirmation to add, update or delete a property",
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
    action_group = parser.add_argument_group()
    action_group.add_argument(
        "-A",
        "--add",
        action="append_const",
        dest="actions",
        const="add",
        help="add new properties from patches",
    )
    action_group.add_argument(
        "-D",
        "--delete",
        action="append_const",
        dest="actions",
        const="delete",
        help="delete properties not in patches",
    )
    action_group.add_argument(
        "-U",
        "--update",
        action="append_const",
        dest="actions",
        const="update",
        help="update properties from patches",
    )
    parser.add_argument(
        "-p",
        "--patch",
        action="append",
        type=Path,
        metavar="patch.properties",
        required=True,
        help="patch file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="output.properties",
        help="modified file",
    )
    parser.add_argument(
        "source",
        type=Path,
        metavar="source.properties",
        help="file to modify",
    )

    args = parser.parse_args(argv)
    if args.actions is None:
        parser.error(
            "at least one action is required --add|-A, --update|-U, --delete|-D"
        )

    output_content = [] if args.output else None

    def confirm(message: str, force: bool = False):
        if force or args.interactive:
            while True:
                answer = input(f"💬  {message} [Y/n] ")
                print(Cursor.UP(), clear_line(), sep="", end="")
                if answer.lower() in ("y", ""):
                    return True
                if answer.lower() == "n":
                    return False
        return True

    def print_line(line: str, style: str = ""):
        """
        print a line with optional color, and keep it to write outputfile at the end
        """
        if output_content is not None:
            output_content.append(line)
        print(
            f"{style if args.color else ''}{line}{Style.RESET_ALL if args.color else ''}"
        )

    def quote(data: dict, key: str):
        text = data.get(key, "")
        return f'"{text}"' if args.quote else text

    try:
        patches = {}
        for patch in args.patch:
            patches.update(properties_to_dict(patch, separator=args.sep))

        date = datetime.now().isoformat(timespec="seconds", sep=" ")
        source_keys = []
        for lineno, line in enumerate(args.source.read_text().splitlines(), 1):
            try:
                key, value = parse_line(line.strip(), separator=args.sep)
                source_keys.append(key)
                if key is None:
                    # comment or blank line
                    print_line(line, Style.DIM)
                elif key not in patches:
                    if "delete" in args.actions and confirm(
                        f"Delete {Fore.RED}{line}{Fore.RESET} ?"
                    ):
                        # delete or comment the line
                        if args.comments:
                            print_line(f"# {date}  remove: {line}", style=Fore.RED)
                    else:
                        # discard change, keep the line
                        print_line(line)
                elif value != patches[key]:
                    if "update" in args.actions and confirm(
                        f"Update {Fore.YELLOW}{key}={Fore.RESET}{Fore.RED}{value}{Fore.RESET},{Fore.GREEN}{patches[key]}{Fore.RESET} ?"
                    ):
                        # update the line
                        if args.comments:
                            print_line(
                                f"# {date}  update: {line}",
                                style=Fore.YELLOW,
                            )
                        print_line(
                            f"{key}{args.sep}{quote(patches, key)}", style=Fore.YELLOW
                        )
                    else:
                        # discard change, keep the line
                        print_line(line)
                else:
                    # same key/value, keep the line
                    print_line(line)
            except ValueError as ex:
                raise syntax_error(ex, args.source, line, lineno)

        # add new properties
        if "add" in args.actions:
            for key, value in patches.items():
                line = f"{key}{args.sep}{quote(patches, key)}"
                if key not in source_keys and confirm(
                    f"Add {Fore.GREEN}{line}{Fore.RESET} ?"
                ):
                    # add property
                    if args.comments:
                        print_line(f"# {date}  add: {key}", style=Fore.GREEN)
                    print_line(line, style=Fore.GREEN)

        if output_content and len(output_content) > 0 and args.output is not None:
            if (
                not args.output.exists()
                or args.force
                or confirm(
                    f"Output file already exists: {args.output}, fo you want to overwrite it?",
                    force=True,
                )
            ):
                args.output.write_text("\n".join(output_content) + "\n")

    except BaseException as exc:
        print(f"{Fore.RED}ERROR: {exc}{Fore.RESET}", file=sys.stderr)
        if isinstance(exc, SyntaxError):
            print(
                f"{Fore.YELLOW}{exc.filename}:{exc.lineno}{Fore.RESET}  {exc.text}",
                file=sys.stderr,
            )
        sys.exit(1)
