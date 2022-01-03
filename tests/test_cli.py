import pytest
from properties_diff.cli import run

SAMPLE1 = "tests/sample1.properties"
SAMPLE1_ALT = "tests/sample1_alt.properties"
SAMPLE2 = "tests/sample2.properties"


def test_missingargs(capsys):
    with pytest.raises(SystemExit):
        run([SAMPLE1])


def test_samefile(capsys):
    run([SAMPLE1, SAMPLE1])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 0


def test_altfile(capsys):
    run([SAMPLE1, SAMPLE1_ALT])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 0


def test_differentfile(capsys):
    run([SAMPLE1, SAMPLE2])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 15
    assert len(captured.err.splitlines()) == 0


def test_differentfile_quiet(capsys):
    run(["--quiet", SAMPLE1, SAMPLE2])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 9
    assert len(captured.err.splitlines()) == 0


def test_differentfile_group(capsys):
    run(["--group", SAMPLE1, SAMPLE2])
    captured_group = capsys.readouterr()
    assert len(captured_group.out.splitlines()) == 15
    assert len(captured_group.err.splitlines()) == 0

    run([SAMPLE1, SAMPLE2])
    captured_nogroup = capsys.readouterr()
    assert len(captured_nogroup.out.splitlines()) == 15
    assert len(captured_nogroup.err.splitlines()) == 0

    assert captured_group.out.splitlines() != captured_nogroup.out.splitlines()
