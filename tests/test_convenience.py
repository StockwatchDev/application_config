"""Test the module application_settings.convenience"""

import pytest
import sys

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock, patch

from application_settings._private.file_operations import FileFormat
from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.convenience import (
    _get_config_class,
    _get_module,
    _get_module_from_file,
    _get_settings_class,
    config_filepath_from_cli,
    parameters_folderpath_from_cli,
    settings_filepath_from_cli,
    use_standard_logging,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class MockParameterContainerProtocolClass:

    @staticmethod
    def kind() -> ParameterKind:
        return ParameterKind.CONFIG

    @classmethod
    def kind_string(cls) -> ParameterKindStr:
        return "Config"

    @classmethod
    def get(cls) -> Self:
        return cls()

    @classmethod
    def get_without_load(cls) -> None:
        pass

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        return cls()

    def _set(self) -> Self:
        return self

    @classmethod
    def default_file_format(cls) -> FileFormat:
        return FileFormat.JSON

    @classmethod
    def default_foldername(cls) -> str:
        return "a folder"

    @classmethod
    def default_filename(cls) -> str:
        return " a filename"

    @classmethod
    def default_filepath(cls) -> Optional[Path]:
        return None

    @classmethod
    def set_filepath(cls, file_path: str = "", load: bool = False) -> None:
        return None

    @classmethod
    def filepath(cls) -> Optional[Path]:
        return None

    @classmethod
    def load(cls, throw_if_file_not_found: bool = False) -> Self:
        return cls()

    def _save(self) -> Self:
        return self


class MockUpdateableParameterContainerProtocolClass(
    MockParameterContainerProtocolClass
):
    @classmethod
    def update(cls, changes: dict[str, Any]) -> Self:
        return cls()


class MockConfigClass(MockParameterContainerProtocolClass):
    pass


class MockSettingsClass(MockUpdateableParameterContainerProtocolClass):
    pass


def test_get_module_from_file_valid() -> None:
    with patch("application_settings.convenience.importlib.util") as mock_importlib:
        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_importlib.spec_from_file_location.return_value = mock_spec
        mock_importlib.module_from_spec.return_value = mock_module
        qualified_classname = "path.to.module.ClassName"
        assert _get_module_from_file(qualified_classname) == mock_module


def test_get_module_from_file_invalid() -> None:
    with patch("application_settings.convenience.importlib.util") as mock_importlib:
        mock_importlib.spec_from_file_location.return_value = None
        qualified_classname = "invalid.module.ClassName"
        assert _get_module_from_file(qualified_classname) is None


def test_get_module_valid() -> None:
    with patch(
        "application_settings.convenience.importlib.import_module"
    ) as mock_import_module:
        mock_module = MagicMock()
        mock_import_module.return_value = mock_module
        qualified_classname = "valid.module.ClassName"
        assert _get_module(qualified_classname) == mock_module


def test_get_module_invalid() -> None:
    with patch(
        "application_settings.convenience.importlib.import_module"
    ) as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        qualified_classname = "invalid.module.ClassName"
        assert _get_module(qualified_classname) is None


def test_get_module_invalid_no_package() -> None:
    qualified_classname = "ClassName"
    assert _get_module(qualified_classname) is None


def test_get_module_invalid_local() -> None:
    with patch(
        "application_settings.convenience._get_module_from_file"
    ) as mock_import_module:
        mock_import_module.return_value = None
        qualified_classname = ".ClassName"
        assert _get_module(qualified_classname) is None


def test_get_config_class_valid() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is MockConfigClass  # type: ignore[comparison-overlap]


def test_get_config_class_invalid_settings() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockSettingsClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_not_subclass() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        class MockConfigClass2:
            pass

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass2)

        qualified_classname = "valid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_missing_class() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        # Simuleer een module zonder de verwachte klasse
        mock_module = MagicMock()
        mock_get_module.return_value = mock_module
        setattr(mock_module, "MissingClass", None)

        # Controleer dat de functie `None` retourneert als de klasse ontbreekt
        qualified_classname = "valid.module.MissingClass"
        assert _get_config_class(qualified_classname) is None


def test_get_config_class_invalid_no_module() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_get_module.return_value = None

        qualified_classname = "invalid.module.ClassName"
        assert _get_config_class(qualified_classname) is None


def test_get_settings_class_valid() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockSettingsClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_settings_class(qualified_classname) is MockSettingsClass  # type: ignore[comparison-overlap]


def test_get_settings_class_invalid_not_subclass() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        # Simuleer een module met een ongeldige klasse
        mock_module = MagicMock()

        mock_get_module.return_value = mock_module
        setattr(mock_module, "ClassName", MockConfigClass)

        qualified_classname = "valid.module.ClassName"
        assert _get_settings_class(qualified_classname) is None


def test_get_settings_class_invalid_missing_class() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_module = MagicMock()
        mock_get_module.return_value = mock_module
        setattr(mock_module, "MissingClass", None)

        qualified_classname = "valid.module.MissingClass"
        assert _get_settings_class(qualified_classname) is None


def test_get_settings_class_invalid_no_module() -> None:
    with patch("application_settings.convenience._get_module") as mock_get_module:
        mock_get_module.return_value = None

        qualified_classname = "invalid.module.ClassName"
        assert _get_settings_class(qualified_classname) is None


def test_config_filepath_from_cli_no_input() -> None:
    parser = ArgumentParser()
    result = config_filepath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_config_filepath_from_cli() -> None:
    parser = ArgumentParser()
    with patch(
        "application_settings.convenience.ArgumentParser.parse_known_args"
    ) as mock_parse_args:
        # Stel een gesimuleerde args in met een gewenst attribuut
        mock_args = MagicMock()
        setattr(mock_args, "config_filepath", ["/mock/path/to/config"])
        mock_parse_args.return_value = (mock_args, [])
        with pytest.raises(ValueError):
            config_filepath_from_cli(parser=parser)


def test_settings_filepath_from_cli_no_input() -> None:
    parser = ArgumentParser()
    result = settings_filepath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_settings_filepath_from_cli() -> None:
    parser = ArgumentParser()
    with patch(
        "application_settings.convenience.ArgumentParser.parse_known_args"
    ) as mock_parse_args:
        # Stel een gesimuleerde args in met een gewenst attribuut
        mock_args = MagicMock()
        setattr(mock_args, "settings_filepath", ["/mock/path/to/settings"])
        mock_parse_args.return_value = (mock_args, [])
        with pytest.raises(ValueError):
            settings_filepath_from_cli(parser=parser)


def test_parameters_folderpath_from_cli() -> None:
    parser = ArgumentParser()
    result = parameters_folderpath_from_cli(parser=parser)
    assert isinstance(result, ArgumentParser)


def test_use_standard_logging() -> None:
    with patch("application_settings.convenience.logger") as mock_logger:
        use_standard_logging(enable=True)
        mock_logger.remove.assert_called_once()
        mock_logger.add.assert_called_once()
        mock_logger.enable.assert_called_once()
