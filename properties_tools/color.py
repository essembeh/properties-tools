# pylint: disable=missing-function-docstring,missing-module-docstring
import sys
from dataclasses import dataclass
from typing import Any, Optional

from colorama import Fore, Style


@dataclass
class Color:
    """
    Easy way to print optionally colored messages
    """

    enabled: bool

    def __post_init__(self):
        if self.enabled is None:
            self.enabled = sys.stdin.isatty()

    def _tostring(self, *messages: str, style: Optional[str] = None, sep: str = " "):
        text = sep.join(map(str, messages))
        if self.enabled and style:
            return f"{style}{text}{Style.RESET_ALL}"
        return text

    def red(self, *data: Any, **kwargs):
        return self._tostring(*data, style=Fore.RED, **kwargs)

    def green(self, *data: Any, **kwargs):
        return self._tostring(*data, style=Fore.GREEN, **kwargs)

    def yellow(self, *data: Any, **kwargs):
        return self._tostring(*data, style=Fore.YELLOW, **kwargs)

    def blue(self, *data: Any, **kwargs):
        return self._tostring(*data, style=Fore.BLUE, **kwargs)

    def grey(self, *data: Any, **kwargs):
        return self._tostring(*data, style=Style.DIM, **kwargs)
