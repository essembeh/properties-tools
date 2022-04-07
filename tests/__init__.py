from shlex import split
from typing import Callable

SAMPLE1 = "tests/sample1.properties"
SAMPLE1_ALT = "tests/sample1_alt.properties"
SAMPLE2 = "tests/sample2.properties"
SAMPLE3 = "tests/sample3.properties"


def execute(run_fnc: Callable, capsys, command: str):
    """
    Execute en entrypoint
    """
    run_fnc(split(command))
    captured = capsys.readouterr()
    return captured.out.splitlines(), captured.err.splitlines()
