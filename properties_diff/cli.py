#!/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict

from colorama import Fore


def properties_to_dict(file: Path, separator="=", comment_char="#") -> Dict[str, str]:
    if not file.exists():
        raise FileExistsError(f"Cannot find file {Fore.YELLOW}{file}{Fore.RESET}")
    out = {}
    for line in map(str.strip, file.read_text().splitlines()):
        if len(line) == 0:
            # empty line
            pass
        elif line.startswith(comment_char):
            # comment line
            pass
        elif separator not in line:
            # invalid line
            raise SyntaxError(
                f"Invalid line in {Fore.YELLOW}{file}{Fore.RESET}: {Fore.RED}{line}{Fore.RESET}"
            )
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
    parser.add_argument("-q", "--quiet", action="store_true", help="less verbose")
    parser.add_argument(
        "-p", "--pretty", action="store_true", help='print properties as key = "value"'
    )
    parser.add_argument(
        "-g",
        "--group-updated",
        action="store_true",
        help="group updated properties",
    )
    parser.add_argument(
        "left", type=Path, metavar="left.properties", help="left file to compare"
    )
    parser.add_argument(
        "right", type=Path, metavar="right.properties", help="right file to compare"
    )

    args = parser.parse_args(args)

    prefix_added, prefix_removed = "+ ", "- "
    if args.quiet:
        prefix_added, prefix_removed = "", ""

    def print_kv(data: dict, key: str):
        if args.pretty:
            return f'{key} = "{data[key]}"'
        return f"{key}={data[key]}"

    try:
        left = properties_to_dict(args.left)
        assert (
            len(left) > 0
        ), f"Cannot find any property in {Fore.YELLOW}{args.left}{Fore.RESET}"
        right = properties_to_dict(args.right)
        assert (
            len(right) > 0
        ), f"Cannot find any property in {Fore.YELLOW}{args.right}{Fore.RESET}"

        added = [key for key in sorted(right) if key not in left]
        if len(added):
            print(f"{Fore.BLUE}Added properties in {args.right}")
            if not args.quiet:
                print(f"{Fore.YELLOW}--- {args.left}{Fore.RESET}")
                print(f"{Fore.YELLOW}+++ {args.right}{Fore.RESET}")
            for key in added:
                print(f"{Fore.GREEN}{prefix_added}{print_kv(right, key)}{Fore.RESET}")

        removed = [key for key in sorted(left) if key not in right]
        if len(removed):
            print(f"{Fore.BLUE}Removed properties from {args.left}")
            if not args.quiet:
                print(f"{Fore.YELLOW}--- {args.left}{Fore.RESET}")
                print(f"{Fore.YELLOW}+++ {args.right}{Fore.RESET}")
            for key in removed:
                print(f"{Fore.RED}{prefix_removed}{print_kv(left, key)}{Fore.RESET}")

        updated = [
            key for key in sorted(left) if key in right and left[key] != right[key]
        ]
        if len(updated):
            print(
                f"{Fore.BLUE}Updated properties from {args.left} to {args.right}{Fore.RESET}"
            )
            if not args.quiet:
                print(f"{Fore.YELLOW}--- {args.left}{Fore.RESET}")
                print(f"{Fore.YELLOW}+++ {args.right}{Fore.RESET}")
            if args.group_updated:
                for key in updated:
                    print(
                        f"{Fore.RED}{prefix_removed}{print_kv(left, key)}{Fore.RESET}"
                    )
                for key in updated:
                    print(
                        f"{Fore.GREEN}{prefix_added}{print_kv(right, key)}{Fore.RESET}"
                    )
            else:
                for key in updated:
                    print(
                        f"{Fore.RED}{prefix_removed}{print_kv(left, key)}{Fore.RESET}"
                    )
                    print(
                        f"{Fore.GREEN}{prefix_added}{print_kv(right, key)}{Fore.RESET}"
                    )
    except BaseException as e:
        print(e, file=sys.stderr)
        sys.exit(1)
