# pylint: disable=missing-function-docstring,unused-import,redefined-outer-name
"""
test for diff cli
"""
from pathlib import Path
from shlex import split

import pytest
from properties_tools import __version__
from properties_tools.diff import run

from . import TEMPLATES_DIR, assert_capsys, samples


def template(filename: str):
    return TEMPLATES_DIR / __name__ / filename


def test_version(capsys):
    with pytest.raises(SystemExit):
        run(split("--version"))
    assert __version__ in capsys.readouterr().out


def test_missingargs(samples: Path):
    with pytest.raises(SystemExit):
        run(split(f"{samples / 'sample1.properties'}"))


def test_bad_sep(capsys, samples: Path):
    with pytest.raises(SystemExit):
        run(
            split(
                f"{samples / 'sample1.properties'} {samples / 'sample1.properties'} --sep /"
            )
        )
    assert_capsys(
        capsys,
        samples,
        stdout_reference="",
        stderr_reference=template("test_bad_sep.err"),
    )


def test_samefile(capsys, samples: Path):
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample1.properties'}"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_samefile.out"),
        stderr_reference="",
    )


def test_altfile(capsys, samples: Path):
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample1_alt.properties'}"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_altfile.out"),
        stderr_reference="",
    )


def test_simple(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode simple"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_simple.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --simple"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_simple.out"),
        stderr_reference="",
    )


def test_diff(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode diff"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_diff.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --diff"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_diff.out"),
        stderr_reference="",
    )


def test_wdiff(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode wdiff"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_wdiff.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --wdiff"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_wdiff.out"),
        stderr_reference="",
    )


def test_quiet(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --quiet"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_quiet.out"),
        stderr_reference="",
    )


def test_quote(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -m diff"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_quote_noquote.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'}  -m diff --quote"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_quote_withquote.out"),
        stderr_reference="",
    )


def test_sections(capsys, samples: Path):
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -A"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_A.out"),
        stderr_reference="",
    )
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -D"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_D.out"),
        stderr_reference="",
    )
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -U"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_U.out"),
        stderr_reference="",
    )
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -AD"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_AD.out"),
        stderr_reference="",
    )
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -AU"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_AU.out"),
        stderr_reference="",
    )
    run(split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -DU"))
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_DU.out"),
        stderr_reference="",
    )
    run(
        split(f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} -ADU")
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_sections_ADU.out"),
        stderr_reference="",
    )


def test_colors(capsys, samples: Path):
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode simple --color"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_colors_simple.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode wdiff --color"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_colors_wdiff.out"),
        stderr_reference="",
    )
    run(
        split(
            f"{samples / 'sample1.properties'} {samples / 'sample2.properties'} --mode diff --color"
        )
    )
    assert_capsys(
        capsys,
        samples,
        stdout_reference=template("test_colors_diff.out"),
        stderr_reference="",
    )
