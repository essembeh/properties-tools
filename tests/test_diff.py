# pylint: disable=missing-function-docstring
"""
test for diff cli
"""


from shlex import split

import pytest
from properties_tools.diff import run
from properties_tools.utils import file_date

from . import *


def template(filename: str):
    return TEMPLATES_DIR / __name__ / filename


def keywords(**files):
    out = {}
    for key, value in files.items():
        out[key] = value
        out[key + "_date"] = file_date(value)
    return out


def test_missingargs(sample1):
    with pytest.raises(SystemExit):
        run(split(f"{sample1}"))


def test_bad_sep(capsys, sample1):
    with pytest.raises(SystemExit):
        run(split(f"{sample1} {sample1} --sep /"))
    assert_capsys(
        capsys,
        stdout_reference="",
        stderr_reference=template("test_bad_sep.err"),
        format_keywords=keywords(left=sample1),
    )


def test_samefile(capsys, sample1):
    run(split(f"{sample1} {sample1}"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_samefile.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1),
    )


def test_altfile(capsys, sample1, sample1_alt):
    run(split(f"{sample1} {sample1_alt}"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_altfile.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample1_alt),
    )


def test_simple(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} --mode simple"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_simple.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )


def test_diff(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} --mode diff"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_diff.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )


def test_wdiff(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} --mode wdiff"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_wdiff.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )


def test_quiet(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} --quiet"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_quiet.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )


def test_quote(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} -m diff"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_quote_noquote.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2}  -m diff --quote"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_quote_withquote.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )


def test_sections(capsys, sample1, sample2):
    run(split(f"{sample1} {sample2} -A"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_A.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -D"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_D.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -U"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_U.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -AD"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_AD.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -AU"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_AU.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -DU"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_DU.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
    run(split(f"{sample1} {sample2} -ADU"))
    assert_capsys(
        capsys,
        stdout_reference=template("test_sections_ADU.out"),
        stderr_reference="",
        format_keywords=keywords(left=sample1, right=sample2),
    )
