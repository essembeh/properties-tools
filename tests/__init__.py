from os import getenv
from pathlib import Path
from re import fullmatch
from shutil import copy
from typing import Any, Dict, Optional, Union

from pytest import fixture

TEMPLATES_DIR = Path(__file__).parent / "templates"


def sample(filename: str, tmp_path):
    ref = Path(__file__).parent / filename
    out = tmp_path / ref.name
    assert not out.exists()
    copy(ref, out)
    from time import sleep

    if getenv("PYTEST_INIT_REFERENCE_FILES") == "1":
        # to have different timestamps
        sleep(1)
    return out


@fixture
def sample1(tmp_path):
    return sample("sample1.properties", tmp_path)


@fixture
def sample1_alt(tmp_path):
    return sample("sample1_alt.properties", tmp_path)


@fixture
def sample2(tmp_path):
    return sample("sample2.properties", tmp_path)


@fixture
def sample3(tmp_path):
    return sample("sample3.properties", tmp_path)


def assert_capsys(
    capsys,
    stdout_reference: Optional[Union[Path, str]] = None,
    stderr_reference: Optional[Union[Path, str]] = None,
    format_keywords: Optional[Dict[str, Any]] = None,
):
    captured = capsys.readouterr()
    assert_out(captured.out, stdout_reference, format_keywords=format_keywords)
    assert_out(captured.err, stderr_reference, format_keywords=format_keywords)


def assert_out(
    content: str,
    reference: Optional[Union[Path, str]],
    format_keywords: Optional[Dict[str, Any]] = None,
):
    if reference is None:
        # no check
        pass
    elif isinstance(reference, str):
        assert content == reference
    else:
        assert isinstance(reference, Path)
        if getenv("PYTEST_INIT_REFERENCE_FILES") == "1":
            reference.parent.mkdir(exist_ok=True, parents=True)
            if format_keywords:
                lines = []
                for line in content.splitlines():
                    line2 = line
                    for key, value in format_keywords.items():
                        line2 = line2.replace(str(value), "{" + key + "}")
                    if line != line2:
                        line = "format:" + line2
                    lines.append(line + "\n")
                content = "".join(lines)
            reference.write_text(content)
        else:
            assert (
                reference.exists()
            ), "Init template with PYTEST_INIT_REFERENCE_FILES=1"
            content_lines = content.splitlines()
            reference_lines = reference.read_text().splitlines()
            assert len(content_lines) == len(
                reference_lines
            ), f"missing lines: {len(content_lines)} != {len(reference_lines)}"

            for line, ref in zip(content_lines, reference_lines):
                ref_items = ref.split(":", 1)
                if len(ref_items) == 2 and ref_items[0] in (
                    "ignore",
                    "matches",
                    "starts",
                    "ends",
                    "contains",
                    "format",
                ):
                    ref_action, ref_value = ref_items[0], ref_items[1]
                    if ref_action == "ignore":
                        pass
                    elif ref_action == "matches":
                        assert fullmatch(
                            ref_value, line
                        ), f"{line.encode()} does not match {ref_value.encode()}"
                    elif ref_action == "starts":
                        assert line.startswith(
                            ref_value
                        ), f"{line.encode()} does not start with {ref_value.encode()}"
                    elif ref_action == "ends":
                        assert line.endswith(
                            ref_value
                        ), f"{line.encode()} does not end with {ref_value.encode()}"
                    elif ref_action == "contains":
                        assert (
                            ref_value in line
                        ), f"{line.encode()} does not contain {ref_value.encode()}"
                    elif ref_action == "format":
                        assert format_keywords is not None
                        ref_value = ref_value.format(**format_keywords)
                        assert (
                            line == ref_value
                        ), f"{line.encode()} is not {ref_value.encode()}"
                    else:
                        assert False, f"Unknown action {ref_action}"
                else:
                    assert line == ref, f"{line.encode()} is not {ref.encode()}"
