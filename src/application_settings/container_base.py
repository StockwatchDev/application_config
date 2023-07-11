"""Base class for a container (= root section) for configuration and settings."""
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict
from enum import Enum, unique
from pathlib import Path
from re import sub
from typing import Any

import tomli_w
from pathvalidate import is_valid_filepath

from application_settings.container_section_base import ContainerSectionBase
from application_settings.type_notation_helper import PathOpt, PathOrStr

if sys.version_info >= (3, 11):
    import tomllib
    from typing import Self
else:
    import tomli as tomllib
    from typing_extensions import Self


@unique
class FileFormat(Enum):
    """File formats that are supported by application_settings"""

    TOML = "toml"
    JSON = "json"


class ContainerBase(ContainerSectionBase, ABC):
    """Base class for Config and Settings container classes"""

    @classmethod
    @abstractmethod
    def default_file_format(cls) -> FileFormat:
        """Return the default file format"""

    @classmethod
    def default_foldername(cls) -> str:
        """Return the class name without kind_string, lowercase, with a preceding dot and underscores to seperate words."""
        if (kind_str := cls.kind_string()) == cls.__name__:
            return f".{kind_str.lower()}"
        return (
            "."
            + sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__.replace(kind_str, "")).lower()
        )

    @classmethod
    def default_filename(cls) -> str:
        """Return the kind_string, lowercase, with the extension that fits the file_format."""
        return f"{cls.kind_string().lower()}.{cls.default_file_format().value}"

    @classmethod
    def default_filepath(cls) -> PathOpt:
        """Return the fully qualified default path for the config/settingsfile

        E.g. ~/.example/config.toml.
        If you prefer to not have a default path then overwrite this method and return None.
        """
        return Path.home() / cls.default_foldername() / cls.default_filename()

    @classmethod
    def set_filepath(cls, file_path: PathOrStr = "", load: bool = False) -> None:
        """Set the path for the file (a singleton).

        Raises:

        * ValueError: if file_path is not a valid path for the OS running the code
        """

        path: PathOpt = None
        if isinstance(file_path, Path):
            path = file_path.resolve()
        elif file_path:
            if is_valid_filepath(file_path, platform="auto"):
                path = Path(file_path).resolve()
            else:
                raise ValueError(
                    f"Given path: '{file_path}' is not a valid path for this OS"
                )

        if path:
            _ALL_PATHS[id(cls)] = path
        else:
            _ALL_PATHS.pop(id(cls), None)

        if load:
            cls.load()
        else:
            if cls._get() is not None:
                print(
                    f"Warning: filepath has been set the but file is not loaded into the {cls.kind_string()}."
                )

    @classmethod
    def filepath(cls) -> PathOpt:
        """Return the path for the file that holds the config / settings."""
        return _ALL_PATHS.get(id(cls), cls.default_filepath())

    @classmethod
    def load(cls, throw_if_file_not_found: bool = False) -> Self:
        """Create a new singleton, try to load parameter values from file.

        Raises:

        * FileNotFoundError: if throw_if_file_not_found == True and filepath() cannot be resolved
        * TOMLDecodeError: if FileFormat == TOML and the file is not a valid toml document
        * JSONDecodeError: if FileFormat == JSON and the file is not a valid json document
        * ValidationError: if a parameter value in the file cannot be coerced into the specified parameter type
        """
        return cls._create_instance(throw_if_file_not_found)

    @classmethod
    def _create_instance(cls, throw_if_file_not_found: bool = False) -> Self:
        """Load stored data, instantiate the Container with it, store it in the singleton and return it."""

        # get whatever is stored in the config/settings file
        data_stored = cls._get_saved_data(throw_if_file_not_found)
        # instantiate and store the Container with the stored data
        return cls.set(data_stored)

    def _update(self, changes: dict[str, Any]) -> Self:
        """Update and save the settings with data specified in changes; not meant for config"""
        return (
            super()  # pylint: disable=protected-access,no-member
            ._update(changes)
            ._save()
        )

    def _save(self) -> Self:
        """Private method to save the singleton to file."""
        if path := self.filepath():
            path.parent.mkdir(parents=True, exist_ok=True)
            if (ext := path.suffix[1:].lower()) == FileFormat.TOML.value:
                with path.open(mode="wb") as fptr:
                    # in self._set(), which normally is always executed, we ensured that
                    # self is a dataclass instance
                    tomli_w.dump(asdict(self), fptr)  # type: ignore[call-overload]
            elif ext == FileFormat.JSON.value:
                with path.open(mode="w") as fptr:
                    # in self._set(), which normally is always executed, we ensured that
                    # self is a dataclass instance
                    json.dump(asdict(self), fptr)  # type: ignore[call-overload]
            else:
                print(f"Unknown file format {ext} given in {path}.")
        else:
            # This situation can occur if no valid path was given as an argument, and
            # the default path is set to None.
            raise RuntimeError(
                f"No path specified for {self.kind_string().lower()} file, cannot be saved."
            )
        return self

    @classmethod
    def _get_saved_data(cls, throw_if_file_not_found: bool = False) -> dict[str, Any]:
        """Get the data stored in the parameter file"""
        data_stored: dict[str, Any] = {}
        path = cls.filepath()
        if path is None or not path.is_file():
            err_mess = (
                f"Path {str(path)} not valid for {cls.kind_string().lower()} file."
            )
            if throw_if_file_not_found:
                raise FileNotFoundError(err_mess)
            print(err_mess, "Trying with defaults, but this may not work.")
            return {}

        if (ext := path.suffix[1:].lower()) == str(FileFormat.TOML.value):
            data_stored = _load_toml_with_includes(path, throw_if_file_not_found)
        elif ext == str(FileFormat.JSON.value):
            with path.open(mode="r") as fptr:
                data_stored = json.load(fptr)
        else:
            print(f"Unknown file format {ext} given in {path}.")
        return data_stored


def _load_toml_with_includes(
    path: Path, throw_if_file_not_found: bool
) -> dict[str, Any]:
    with path.open(mode="rb") as fptr:
        data_stored = tomllib.load(fptr)
    if included_files := data_stored.get("__include__", None):
        if isinstance(str, included_files):
            included_files = [included_files]
        for included_file in included_files:
            if is_valid_filepath(included_file, platform="auto"):
                included_file_path = Path(included_file)
                if not included_file_path.is_absolute():
                    included_file_path = path / included_file_path
                included_file_path.resolve()
                if not included_file_path.is_file():
                    err_mess = (
                        f"Path {str(included_file_path)} not valid for toml file."
                    )
                    if throw_if_file_not_found:
                        raise FileNotFoundError(err_mess)
                    print(err_mess, "Trying with defaults, but this may not work.")
                else:
                    with included_file_path.open(mode="rb") as fptr:
                        data_stored = data_stored | tomllib.load(fptr)
            else:
                raise ValueError(
                    f"Given path: '{included_file}' is not a valid path for this OS"
                )
    return data_stored


_ALL_PATHS: dict[int, PathOpt] = {}
