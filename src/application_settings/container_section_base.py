"""Abstract base class for sections to be added to containers and container sections for configuration and settings."""

import sys
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import Any, Optional, cast

from loguru import logger
from pydantic.dataclasses import is_pydantic_dataclass

from application_settings.parameter_kind import ParameterKind, ParameterKindStr
from application_settings.parametrization import log_level
from application_settings.protocols import ParameterContainerSectionProtocol

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class ParameterContainerSectionBase(ABC):
    """Base class for all ParameterContainerSection classes"""

    @staticmethod
    @abstractmethod
    def kind() -> ParameterKind:
        """Return either ParameterKind.CONFIG or ParameterKind.SETTINGS"""
        # method defined here because it is called by cls.kind_string()

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
        # get() is called on a Section but the application
        # has not yet created or loaded a config.
        logger.log(
            log_level(cls.kind()),
            f"{cls.kind_string()} section {cls.__name__} accessed before data has been loaded; "
            f"will try to load via command line parameter '--{cls.__name__}_file'",
        )

    @classmethod
    def set(cls, data: dict[str, Any]) -> Self:
        """Create a new dataclass instance using data and set the singleton."""
        new_instance = cls(**data)
        if data:
            new_instance._check_initialized_and_extra(data)
        return new_instance._set()

    @classmethod
    def _get(
        cls,
    ) -> Optional[Self]:  # pylint: disable=consider-alternative-union-syntax
        """Get the singleton."""
        if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
            return cast(Self, the_container)
        return None

    @classmethod
    def _create_instance(
        cls, throw_if_file_not_found: bool = False  # pylint: disable=unused-argument
    ) -> Self:
        """Create a new ParameterContainerSection with default values. May go wrong if section is not zeroconf."""
        return cls.set({})

    def _set(self) -> Self:
        """Store the singleton."""
        _check_dataclass_decorator(self)
        _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
        subsections = [
            attr
            for attr in vars(self).values()
            if isinstance(attr, ParameterContainerSectionProtocol)
        ]
        for subsec in subsections:
            subsec._set()  # pylint: disable=protected-access
        return self

    @staticmethod
    def _is_parameter_container_section(a_field_type: Any) -> bool:
        try:
            return issubclass(a_field_type, ParameterContainerSectionProtocol)
        except TypeError:
            return False

    def _check_initialized_and_extra(
        self, data: dict[str, Any], section_name: str = ""
    ) -> Self:
        """Store the singleton and check if extra parameters were provided and/or parameters were missing."""
        if is_pydantic_dataclass(type(self)):
            section_specifier = (
                f" in section {section_name}"
                if section_name
                else " in the root section"
            )
            field_names = {fld.name for fld in fields(self)}  # type: ignore[arg-type]
            subsection_names = {
                fld.name
                for fld in fields(self)  # type: ignore[arg-type]
                if self._is_parameter_container_section(fld.type)
            }
            uninitialized_field_names = (
                field_names - subsection_names - set(data.keys())
            )
            for uninitialized_field in uninitialized_field_names:
                logger.log(
                    log_level(self.kind()),
                    f"Parameter {uninitialized_field}{section_specifier} initialized with default value.",
                )
            extra_data_fields = set(data.keys()) - field_names
            for extra_data_field in extra_data_fields:
                logger.log(
                    log_level(self.kind()),
                    f"Extra parameter {extra_data_field}{section_specifier} that is not used for initialization.",
                )
            subsections = [
                (
                    subsection_name,
                    cast(
                        ParameterContainerSectionProtocol,
                        getattr(self, subsection_name),
                    ),
                )
                for subsection_name in subsection_names
            ]
            prefix = f"{section_name}." if section_name else ""
            for subsec_name, subsec in subsections:
                sub_data = data.get(subsec_name, {})
                subsec._check_initialized_and_extra(  # pylint: disable=protected-access
                    sub_data, f"{prefix}{subsec_name}"
                )
        return self


def _check_dataclass_decorator(obj: Any) -> None:
    if not (is_pydantic_dataclass(type(obj))):
        raise TypeError(
            f"{obj} is not a pydantic dataclass instance; did you forget to add "
            f"'@dataclass(frozen=True)' when you defined {obj.__class__}?"
        )
    # We don't have to test for frozen=True, because a TypeError will be raised
    # by dataclass anyway if the subclass is not frozen


_ALL_CONTAINER_SECTION_SINGLETONS: dict[int, ParameterContainerSectionProtocol] = {}
