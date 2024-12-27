"""Defines parameters for application_settings"""

# pylint: disable=duplicate-code

import sys
from abc import ABC, abstractmethod
from typing import Any, Optional, cast

from attributes_doc import attributes_doc
from pydantic.dataclasses import dataclass

from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.protocols import ParameterContainerSectionProtocol

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# This is not an example how to implement a ConfigSection
# because class ApplicationSettingsContainerSectionBase (re-)implements all methods of ContainerSectionBase.
# This is done so that this class will meet the ParameterContainerSection protocol
# yet does not inherit from ContainerSectionBase and therewith prevents circular imports.


def log_level(kind: ParameterKind) -> str:
    """Return the log level taking into consideration whether or not strict_mode is applied"""
    # we want to keep a clear else code block for 3.9
    if sys.version_info >= (  # pylint: disable=no-else-raise
        3,
        10,
    ):
        match kind:
            case ParameterKind.CONFIG:
                return (
                    "WARNING" if ApplicationConfigSection.get().strict_mode else "DEBUG"
                )
            case ParameterKind.SETTINGS:
                return (
                    "WARNING"
                    if ApplicationSettingsSection.get().strict_mode
                    else "DEBUG"
                )
        raise ValueError(f"Unknown value {kind} for ParameterKind.")
    else:
        if kind == ParameterKind.CONFIG:
            return "WARNING" if ApplicationConfigSection.get().strict_mode else "DEBUG"
        if kind == ParameterKind.SETTINGS:
            return (
                "WARNING" if ApplicationSettingsSection.get().strict_mode else "DEBUG"
            )
        raise ValueError(f"Unknown value {kind} for ParameterKind.")


class ApplicationSettingsContainerSectionBase(ABC):
    """Behavior for parametrization of the application_settings library package"""

    @staticmethod
    @abstractmethod
    def kind() -> ParameterKind:
        """Return either ParameterKind.CONFIG or ParameterKind.SETTINGS"""

    @classmethod
    def kind_string(cls) -> ParameterKindStr:
        """Return either 'Config' or 'Settings'"""
        return cls.kind().value

    @classmethod
    def get(cls) -> Self:
        """Get the singleton; if not existing, create it. Loading from file only done for a container."""

        if (_the_container_or_none := cls._get()) is None:
            # no config section has been made yet
            cls.get_without_load()
            # so let's instantiate one and keep it in the global store
            return cls._create_instance()
        return _the_container_or_none

    @classmethod
    def get_without_load(cls) -> None:
        """Get has been called on a section before a load was done; handle this."""
        # Don't do anything here

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """Create a new dataclass instance using data and set the singleton."""
        return cls(**data)._set()

    @classmethod
    def _get(
        cls,
    ) -> Optional[Self]:  # pylint: disable=consider-alternative-union-syntax
        """Get the singleton."""
        if the_container := _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS.get(
            id(cls)
        ):
            return cast(Self, the_container)
        return None

    @classmethod
    def _create_instance(
        cls, throw_if_file_not_found: bool = False  # pylint: disable=unused-argument
    ) -> Self:
        """Create a new ContainerSection with default values. Likely that this is wrong."""
        return cls.set({})

    def _set(self) -> Self:
        """Store the singleton."""
        # no need to do the check on dataclass decorator
        _ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = (
            self
        )
        # ApplicationSettingsSection does not have subsections
        return self


@attributes_doc
@dataclass(frozen=True)
class ApplicationSettingsSection(ApplicationSettingsContainerSectionBase):
    """Settings parameters for the application_settings library package"""

    settings_container_class: str = "application_settings.SettingsBase"
    """Class that defines the root container of an application's settings; 
    defaults to 'application_settings.SettingsBase' but should be given an application-specific value"""

    strict_mode: bool = False
    """Whether or not to apply strict mode. In strict mode, warnings rather than debug messages are logged when: 
    1) parameters are accessed before a file is loaded
    2) parameters are missing from the loaded file
    3) unknown parameters are found in the loaded file"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.SETTINGS"""
        return ParameterKind.SETTINGS


@attributes_doc
@dataclass(frozen=True)
class ApplicationConfigSection(ApplicationSettingsContainerSectionBase):
    """Config parameters for the application_settings library package"""

    config_container_class: str = "application_settings.ConfigBase"
    """Class that defines the root container of an application config; 
    defaults to 'application_settings.ConfigBase' but should be given an application-specific value"""

    strict_mode: bool = False
    """Whether or not to apply strict mode. In strict mode, warnings rather than debug messages are logged when: 
    1) parameters are accessed before a file is loaded
    2) parameters are missing from the loaded file
    3) unknown parameters are found in the loaded file"""

    @staticmethod
    def kind() -> ParameterKind:
        """Return ParameterKind.CONFIG"""
        return ParameterKind.CONFIG


_ALL_APPLICATION_SETTINGS_CONTAINER_SECTION_SINGLETONS: dict[
    int, ParameterContainerSectionProtocol
] = {}
"""Can hold the singleton for ApplicationSettingsSection and for ApplicationConfigSection"""


# TODO:
# - silence logging until application settings config has been loaded
