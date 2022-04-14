# pylint: disable=missing-function-docstring,missing-class-docstring
from datetime import datetime
from os import getenv, utime
from pathlib import Path
from re import fullmatch
from shutil import copytree
from typing import Any, Dict, Optional, Union

from pytest import fixture

SAMPLES_DIR = Path(__file__).parent / "samples"
TEMPLATES_DIR = Path(__file__).parent / "templates"
GEN_TEMPLATE = "PYTEST_GEN_TEMPLATE"


def set_mtime(file: Path, date_str: str):
    timestamp = datetime.fromisoformat(date_str).timestamp()
    utime(file, (timestamp, timestamp))


def format_line(text: str, variables: Dict[str, Any]):
    return text.format(**variables)


def unformat_line(text: str, variables: Dict[str, Any]):
    out = text
    for key, value in variables.items():
        out = out.replace(str(value), "{" + key + "}")
    return text if text == out else f"format:{out}"


@fixture
def samples(tmp_path) -> Path:
    out = copytree(SAMPLES_DIR, tmp_path, dirs_exist_ok=True)
    set_mtime(out / "sample1.properties", "2020-12-12T12:00:00")
    set_mtime(out / "sample1_alt.properties", "2020-12-12T12:01:00")
    set_mtime(out / "sample2.properties", "2020-12-12T12:02:00")
    set_mtime(out / "sample3.properties", "2020-12-12T12:03:00")
    return out


def assert_capsys(
    capsys,
    tmp_path: Path,
    stdout_reference: Optional[Union[Path, str]] = None,
    stderr_reference: Optional[Union[Path, str]] = None,
):
    captured = capsys.readouterr()
    assert_out(captured.out, stdout_reference, tmp_path)
    assert_out(captured.err, stderr_reference, tmp_path)


def assert_out(
    content: str,
    reference: Optional[Union[Path, str]],
    tmp_path: Path,
):
    if reference is None:
        # no check
        pass
    elif isinstance(reference, str):
        assert content == reference
    else:
        assert isinstance(reference, Path)
        variables = {"tmp_path": tmp_path}
        if getenv(GEN_TEMPLATE) == "1":
            reference.parent.mkdir(exist_ok=True, parents=True)
            with reference.open("w") as ref:
                for line in content.splitlines():
                    ref.write(unformat_line(line, variables) + "\n")
        else:
            assert reference.exists(), f"Init template with {GEN_TEMPLATE}=1"
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
                        ref_value = format_line(ref_value, variables)
                        assert (
                            line == ref_value
                        ), f"{line.encode()} is not {ref_value.encode()}"
                    else:
                        assert False, f"Unknown action {ref_action}"
                else:
                    assert line == ref, f"{line.encode()} is not {ref.encode()}"
