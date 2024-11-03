"""Module for handling configuration."""

from application_settings.container_base import ParameterContainerBase
from application_settings.container_section_base import ParameterContainerSectionBase
from application_settings.parameter_kind import ParameterKind

from ._private.file_operations import FileFormat


class ConfigSectionBase(ParameterContainerSectionBase):
    """Base class for all ConfigSection classes, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG


class ConfigBase(ParameterContainerBase):
    """Base class for main Config class, implements the abstract methods of the base(s)"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG

    @staticmethod
    def default_file_format() -> FileFormat:
        """Return the default file format"""  # disable=duplicate-code
        return FileFormat.TOML
