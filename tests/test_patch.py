# pylint: disable=missing-function-docstring
"""
test for patch cli
"""


import pytest
from properties_diff.patch import run

from . import SAMPLE1, SAMPLE1_ALT, SAMPLE2, execute

NOT_QUIET = 2
ADDED = 1
DELETED = 1
MODIFIED = 2


def test_bad_sep(capsys):
    with pytest.raises(SystemExit):
        execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1} --add --sep /")
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 2


def test_samefile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1} --add")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out


def test_altfile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1_ALT} --add")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out


def test_update(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -U")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" not in out
    assert "database.host=localhost" in out


def test_add(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -A")
    assert len(out) == 8
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out
    assert "database.version=12" in out
    assert "database.host=localhost" in out


def test_delete(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -D")
    assert len(out) == 6
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out
    assert "database.version=12" not in out
    assert "database.host=localhost" not in out


def test_adu(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -ADU")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" in out
    assert "database.host=localhost" not in out


def test_output(capsys, tmp_path):
    output = tmp_path / "output.properties"
    out, err = execute(
        run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -ADU --output {output} --comments"
    )
    assert len(out) == 11
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" in out
    assert "database.host=localhost" not in out
    assert output.exists()
    assert output.read_text().splitlines() == out
