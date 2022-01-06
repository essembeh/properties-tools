import shlex

import pytest
from properties_diff.cli import run

SAMPLE1 = "tests/sample1.properties"
SAMPLE1_ALT = "tests/sample1_alt.properties"
SAMPLE2 = "tests/sample2.properties"

NOT_QUIET = 2
ADDED = 1
DELETED = 1
MODIFIED = 2


def execute(capsys, command: str):
    run(shlex.split(command))
    captured = capsys.readouterr()
    return captured.out.splitlines(), captured.err.splitlines()


def test_missingargs(capsys):
    with pytest.raises(SystemExit):
        execute(capsys, f"{SAMPLE1}")


def test_bad_sep(capsys):
    with pytest.raises(SystemExit):
        execute(capsys, f"{SAMPLE1} {SAMPLE1} --sep /")
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 2


def test_samefile(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE1}")
    assert len(out) == 1
    assert len(err) == 0


def test_altfile(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE1_ALT}")
    assert len(out) == 1
    assert len(err) == 0


def test_simple(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} --mode simple")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0


def test_diff(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} --mode diff")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0


def test_wdiff(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} --mode wdiff")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + MODIFIED
    assert len(err) == 0


def test_quiet(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} --quiet")
    assert len(out) == 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0


def test_quote(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2}")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0

    out_quote, err_quote = execute(capsys, f"{SAMPLE1} {SAMPLE2} --quote")
    assert len(out_quote) == len(out)
    assert len(err_quote) == len(err)

    for lineno, lines in enumerate(zip(out_quote, out), start=1):
        if lineno in (4, 6, 8, 9, 10, 11):
            assert len(lines[0]) == len(lines[1]) + 2
        else:
            assert len(lines[0]) == len(lines[1])


def test_sections(capsys):
    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -A")
    assert len(out) == NOT_QUIET + 1 + ADDED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -D")
    assert len(out) == NOT_QUIET + 1 + DELETED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -M")
    assert len(out) == NOT_QUIET + 1 + 2 * MODIFIED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -AD")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -AM")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + 2 * MODIFIED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -DM")
    assert len(out) == NOT_QUIET + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0

    out, err = execute(capsys, f"{SAMPLE1} {SAMPLE2} -ADM")
    assert len(out) == NOT_QUIET + 1 + ADDED + 1 + DELETED + 1 + 2 * MODIFIED
    assert len(err) == 0
