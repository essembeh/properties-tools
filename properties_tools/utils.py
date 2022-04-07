from pathlib import Path
from typing import Dict, Optional, Tuple


def parse_line(
    line: str, separator: str = "=", comment_char: str = "#"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a line and return key,value or None if empty line or comment
    """
    if len(line) == 0:
        # empty line
        return (None, None)
    if line.startswith(comment_char):
        # comment line
        return (None, line)
    if separator not in line:
        # invalid line
        raise ValueError(f"no separator '{separator}'")

    # valid line
    index = line.index(separator)
    key = line[0:index].strip()
    value = line[index + len(separator) :].strip()
    if len(value) > 1 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return (key, value)


def properties_to_dict(file: Path, separator="=", comment_char="#") -> Dict[str, str]:
    """
    Parse a properties file and return the dict of key:value
    """
    if not file.exists():
        raise FileExistsError(f"Cannot find file {file}")
    out = {}
    if not separator:
        raise ValueError("Invalid separator")
    for lineno, line in enumerate(map(str.strip, file.read_text().splitlines()), 1):
        try:
            key, value = parse_line(
                line, separator=separator, comment_char=comment_char
            )
            if key is not None:
                out[key] = value
        except ValueError as ex:
            raise syntax_error(ex, file, line, lineno)
    return out


def syntax_error(
    error: BaseException, file: Path, line: str, lineno: int
) -> SyntaxError:
    """
    build a syntax error from any exception raised while parsing a file
    """
    error = SyntaxError(f"Invalid file, {error}' on line {lineno}")
    error.lineno = lineno
    error.filename = str(file)
    error.text = line
    return error
