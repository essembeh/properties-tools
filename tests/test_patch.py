# pylint: disable=missing-function-docstring,unused-import,redefined-outer-name
"""
test for patch cli
"""

from pathlib import Path
from shlex import split

import pytest
from properties_tools import __version__
from properties_tools.patch import run

from . import TEMPLATES_DIR, assert_capsys, samples


def template(filename: str):
    return TEMPLATES_DIR / __name__ / filename


def test_version(capsys):
    with pytest.raises(SystemExit):
        run(split("--version"))
    assert __version__ in capsys.readouterr().out


def test_bad_sep(capsys, samples: Path):
    with pytest.raises(SystemExit):
        run(
            split(
                f"{samples / 'sample1.properties'}  --patch {samples / 'sample1.properties'} --add --sep /"
            )
        )
    assert_capsys(
        capsys,
        samples,
        stdout_reference="",
        stderr_reference=template("test_bad_sep.err"),
    )


def test_samefile(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample1.properties'} --add"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_samefile.out"),
        stderr_reference="",
    )


def test_altfile(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample1_alt.properties'} --add"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_altfile.out"),
        stderr_reference="",
    )


def test_update(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -U"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_update.out"),
        stderr_reference="",
    )


def test_add(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -A"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_add.out"),
        stderr_reference="",
    )


def test_delete(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -D"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_delete.out"),
        stderr_reference="",
    )


def test_adu(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_adu.out"),
        stderr_reference="",
    )


def test_comments(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --comments"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_comments.out"),
        stderr_reference="",
    )


def test_output(capsys, tmp_path, samples: Path):
    output = tmp_path / "output.properties"
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --output {output}"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_output.out"),
        stderr_reference="",
    )
    assert output.exists()
    assert output.read_text() == template("test_output.out").read_text()


def test_no_overwrite(tmp_path, samples: Path):
    output = tmp_path / "output.properties"
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --output {output}"
        )
    )
    assert output.exists()

    with pytest.raises(SystemExit):
        run(
            split(
                f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --output {output}"
            )
        )


def test_in_place(capsys, samples: Path):
    source_text = (samples / "sample1.properties").read_text()
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --overwrite"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_in_place.out"),
        stderr_reference="",
    )
    assert source_text != (samples / "sample1.properties").read_text()
    assert (samples / "sample1.properties").read_text() == template(
        "test_in_place.out"
    ).read_text()


def test_color(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'}  --patch {samples / 'sample2.properties'} -ADU --color --comment"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_color.out"),
        stderr_reference="",
    )
