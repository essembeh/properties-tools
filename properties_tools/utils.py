from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple


@dataclass
class ParsedLine:
    line: str
    separator_char: str = field(default="=")
    comment_char: str = field(default="#")

    def __post_init__(self):
        if (
            len(self.line) > 0
            and not self.is_comment()
            and self.separator_char not in self.line
        ):
            raise ValueError("no separator found")

    def __str__(self):
        return self.line

    @cached_property
    def _elements(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse a line and return key,value,comment or None if empty line
        """
        if len(self.line) == 0:
            # empty line
            return (None, None, None)
        if self.line.startswith(self.comment_char):
            # comment line
            return (None, None, self.line)
        if self.separator_char not in self.line:
            # invalid line
            raise ValueError(f"no separator '{self.separator_char}'")

        # valid line
        key, _, value = self.line.partition(self.separator_char)
        # remove useless whitespaces
        key, value = key.strip(), value.strip()
        # remove optional double quotes
        if len(value) > 1 and value[0] == value[-1] == '"':
            value = value[1:-1]
        return (key, value, None)

    def is_comment(self):
        return self.line.startswith(self.comment_char)

    def is_property(self):
        return self._elements[0] is not None and self._elements[1] is not None

    @property
    def key(self) -> str:
        out = self._elements[0]
        assert out is not None
        return out

    @property
    def value(self) -> str:
        out = self._elements[1]
        assert out is not None
        return out


def file_date(file: Path):
    return datetime.isoformat(
        datetime.fromtimestamp(file.stat().st_mtime), timespec="seconds", sep=" "
    )


def parse_file(
    file: Path, separator: str = "=", comment_char: str = "#"
) -> Generator[ParsedLine, None, None]:
    """
    Parse a properties file and yiels parsed lines
    """
    for lineno, line in enumerate(file.read_text().splitlines(), 1):
        try:
            yield ParsedLine(line, separator_char=separator, comment_char=comment_char)
        except ValueError as ex:
            raise syntax_error(ex, file, line, lineno)


def propertiesfile_to_dict(
    file: Path, separator="=", comment_char="#"
) -> Dict[str, str]:
    """
    Parse a properties file and return the dict of key:value
    """
    if not file.exists():
        raise FileExistsError(f"Cannot find file {file}")
    if not separator:
        raise ValueError("Invalid separator")
    return {
        l.key: l.value
        for l in parse_file(file, separator=separator, comment_char=comment_char)
        if l.is_property()
    }


def syntax_error(
    error: BaseException, file: Path, line: str, lineno: int
) -> SyntaxError:
    """
    build a syntax error from any exception raised while parsing a file
    """
    error = SyntaxError(f"Invalid file, {error}")
    error.lineno = lineno
    error.filename = str(file)
    error.text = line
    return error
