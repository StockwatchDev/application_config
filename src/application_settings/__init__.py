"""Module for loading and retrieving configuration."""

from importlib.metadata import version

from .configuring_base import ConfigBase, ConfigSectionBase, ConfigSectionT, ConfigT
from .settings_base import (
    SettingsBase,
    SettingsSectionBase,
    SettingsSectionT,
    SettingsT,
)
from .type_notation_helper import PathOptT, PathOrStrT

__version__ = version("application_settings")

__all__ = [
    "ConfigSectionT",
    "ConfigT",
    "ConfigSectionBase",
    "ConfigBase",
    "PathOptT",
    "PathOrStrT",
    "SettingsSectionT",
    "SettingsT",
    "SettingsSectionBase",
    "SettingsBase",
]