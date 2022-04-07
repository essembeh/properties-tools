# pylint: disable=missing-function-docstring
"""
test for diff cli
"""

import pytest
from properties_diff.diff import run

from . import SAMPLE1, SAMPLE1_ALT, SAMPLE2, execute

NOT_QUIET = 2
ADDED = 1
DELETED = 1
MODIFIED = 2


def test_missingargs(capsys):
    with pytest.raises(SystemExit):
        execute(run, capsys, f"{SAMPLE1}")


def test_bad_sep(capsys):
    with pytest.raises(SystemExit):
        execute(run, capsys, f"{SAMPLE1} {SAMPLE1} --sep /")
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 2


def test_samefile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE1}")
    assert len(out) == 1
    assert len(err) == 0


def test_altfile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE1_ALT}")
    assert len(out) == 1
    assert len(err) == 0


def test_simple(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} --mode simple")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0


def test_diff(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} --mode diff")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0


def test_wdiff(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} --mode wdiff")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + MODIFIED
    assert len(err) == 0


def test_quiet(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} --quiet")
    assert len(out) == 1 + ADDED + 1 + DELETED + 1 + MODIFIED
    assert len(err) == 0


def test_quote(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -m diff")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0

    out_quote, err_quote = execute(run, capsys, f"{SAMPLE1} {SAMPLE2}  -m diff --quote")
    assert len(out_quote) == len(out)
    assert len(err_quote) == len(err)

    for lineno, lines in enumerate(zip(out_quote, out), start=1):
        if lineno in (4, 6, 8, 9, 10, 11):
            assert len(lines[0]) == len(lines[1]) + 2
        else:
            assert len(lines[0]) == len(lines[1])


def test_sections(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -A")
    assert len(out) == NOT_QUIET + 1 + ADDED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -D")
    assert len(out) == NOT_QUIET + 1 + DELETED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -U")
    assert len(out) == NOT_QUIET + 1 + MODIFIED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -AD")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -AU")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + MODIFIED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -DU")
    assert len(out) == NOT_QUIET + 1 + DELETED + 1 + MODIFIED
    assert len(err) == 0

    out, err = execute(run, capsys, f"{SAMPLE1} {SAMPLE2} -ADU")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + MODIFIED
    assert len(err) == 0
