"""
diff cli tool entrypoint
"""

import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional

from colorama.ansi import Cursor, clear_line

from . import __version__
from .color import Color
from .utils import parse_file, propertiesfile_to_dict


def run(argv: Optional[List[str]] = None):
    """
    patch cli
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
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
        "-c",
        "--comments",
        dest="comments",
        action="store_true",
        help="insert comment when property is added, updated or deleted",
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
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="output.properties",
        help="modified file",
    )
    output_group.add_argument(
        "-w",
        "--overwrite",
        action="store_true",
        help="update input properties file in place",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force output file (--output) overwrite if it already exists",
    )
    parser.add_argument(
        "source",
        type=Path,
        metavar="source.properties",
        help="file to modify",
    )

    args = parser.parse_args(argv)

    color = Color(args.color)

    if args.actions is None:
        parser.error(
            "at least one action is required --add|-A, --update|-U, --delete|-D"
        )

    output_content = [] if args.output or args.overwrite else None

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

    def print_line(line: Any, color_fnc: Optional[Callable] = None):
        """
        print a line with optional color, and keep it to write outputfile at the end
        """
        assert line is not None
        line = str(line)
        if output_content is not None:
            output_content.append(line)
        print(color_fnc(line) if color_fnc else line)

    def quote(data: dict, key: str):
        text = data.get(key, "")
        return f'"{text}"' if args.quote else text

    try:
        # check output file does not exists
        if args.output and args.output.exists():
            raise ValueError(
                "output file already exists, use '--force' to overwrite it"
            )

        patches = {}
        for patch in args.patch:
            patches.update(propertiesfile_to_dict(patch, separator=args.sep))

        date_now = datetime.now().isoformat(timespec="seconds", sep=" ")

        source_keys = []
        for parsed_line in list(parse_file(args.source, separator=args.sep)):
            if parsed_line.is_property():
                source_keys.append(parsed_line.key)

            if not parsed_line.is_property():
                # comment or blank line
                print_line(parsed_line, color.grey)
            elif parsed_line.key not in patches:
                if "delete" in args.actions and confirm(
                    f"Delete {color.red(parsed_line)} ?"
                ):
                    # delete or comment the line
                    if args.comments:
                        print_line(f"# {date_now}  remove: {parsed_line}", color.red)
                else:
                    # discard change, keep the line
                    print_line(parsed_line)
            elif parsed_line.value != patches[parsed_line.key]:
                if "update" in args.actions and confirm(
                    f"Update {color.yellow(parsed_line.key)}={color.red(parsed_line.value)},{color.green(patches[parsed_line.key])} ?"
                ):
                    # update the line
                    if args.comments:
                        print_line(
                            f"# {date_now}  update: {parsed_line}",
                            color.yellow,
                        )
                    print_line(
                        f"{parsed_line.key}{args.sep}{quote(patches, parsed_line.key)}",
                        color.yellow,
                    )
                else:
                    # discard change, keep the line
                    print_line(parsed_line)
            else:
                # same key/value, keep the line
                print_line(parsed_line)

        # add new properties
        if "add" in args.actions:
            for key in patches:
                line = f"{key}{args.sep}{quote(patches, key)}"
                if key not in source_keys and confirm(f"Add {color.green(line)} ?"):
                    # add property
                    if args.comments:
                        print_line(f"# {date_now}  add: {key}", color.green)
                    print_line(line, color.green)

        if output_content and len(output_content) > 0:
            # write output file
            (args.source if args.overwrite else args.output).write_text(
                "\n".join(output_content) + "\n"
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
