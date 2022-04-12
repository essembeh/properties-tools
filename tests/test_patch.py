# pylint: disable=missing-function-docstring
"""
test for patch cli
"""

from shlex import split

import pytest
from properties_tools.patch import run

from . import *


def template(filename: str):
    return TEMPLATES_DIR / __name__ / filename


def test_bad_sep(capsys, sample1):
    with pytest.raises(SystemExit):
        run(split(f"{sample1}  --patch {sample1} --add --sep /"))
    assert_capsys(
        capsys,
        stdout_reference="",
        stderr_reference=template("test_bad_sep.err"),
        format_keywords={"file": sample1},
    )


def test_samefile(capsys, sample1):
    run(split(f"{sample1}  --patch {sample1} --add"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_samefile.out"),
        stderr_reference="",
    )


def test_altfile(capsys, sample1, sample1_alt):
    run(split(f"{sample1}  --patch {sample1_alt} --add"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_altfile.out"),
        stderr_reference="",
    )


def test_update(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -U"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_update.out"),
        stderr_reference="",
    )


def test_add(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -A"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_add.out"),
        stderr_reference="",
    )


def test_delete(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -D"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_delete.out"),
        stderr_reference="",
    )


def test_adu(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -ADU"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_adu.out"),
        stderr_reference="",
    )


def test_comments(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -ADU --comments"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_comments.out"),
        stderr_reference="",
    )


def test_output(capsys, tmp_path, sample1, sample2):
    output = tmp_path / "output.properties"
    run(split(f"{sample1}  --patch {sample2} -ADU --output {output}"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_output.out"),
        stderr_reference="",
    )
    assert output.exists()
    assert output.read_text() == template("test_output.out").read_text()


def test_no_overwrite(tmp_path, sample1, sample2):
    output = tmp_path / "output.properties"
    run(split(f"{sample1}  --patch {sample2} -ADU --output {output}"))
    assert output.exists()

    with pytest.raises(SystemExit):
        run(split(f"{sample1}  --patch {sample2} -ADU --output {output}"))


def test_in_place(capsys, sample1, sample2):
    source_text = sample1.read_text()
    run(split(f"{sample1}  --patch {sample2} -ADU --overwrite"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_in_place.out"),
        stderr_reference="",
    )
    assert source_text != sample1.read_text()
    assert sample1.read_text() == template("test_in_place.out").read_text()


def test_color(capsys, sample1, sample2):
    run(split(f"{sample1}  --patch {sample2} -ADU --color --comment"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_color.out"),
        stderr_reference="",
    )
