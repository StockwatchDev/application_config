# pylint: disable=consider-alternative-union-syntax, useless-suppression
"""Defines type aliases that handle notational differences between python versions."""
import sys
from pathlib import Path
from types import ModuleType

if sys.version_info >= (3, 10):
    from typing import TypeAlias

    PathOrStr: TypeAlias = Path | str
    ModuleTypeOpt: TypeAlias = ModuleType | None
else:
    from typing import Union

    from typing_extensions import TypeAlias

    PathOrStr: TypeAlias = Union[Path, str]
    ModuleTypeOpt: TypeAlias = Union[ModuleType, None]
