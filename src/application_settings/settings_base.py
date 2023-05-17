"""Module for handling settings."""
from pydantic.dataclasses import dataclass

from .container_base import ContainerBase, FileFormat
from .container_section_base import ContainerSectionBase, SectionTypeStr


@dataclass(frozen=True)
class SettingsSectionBase(ContainerSectionBase):
    """Base class for all SettingsSection classes (so that we can bound a TypeVar)"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        "Return 'Settings'"
        return "Settings"


@dataclass(frozen=True)
class SettingsBase(ContainerBase):
    """Base class for main Settings class"""

    @classmethod
    def kind_string(cls) -> SectionTypeStr:
        "Return 'Settings'"
        return "Settings"

    @classmethod
    def default_file_format(cls) -> FileFormat:
        "Return the default file format"
        return FileFormat.JSON
