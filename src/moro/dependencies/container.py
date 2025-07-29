"""Dependency injection container configuration."""

from typing import Callable, TypeVar

from injector import Binder, Injector

from moro.config.settings import ConfigRepository

_T = TypeVar("_T")


def configure(binder: Binder) -> None:
    """Configure the dependency injection container."""


def create_injector(config: ConfigRepository) -> Injector:
    """
    Create and configure the dependency injection container.

    Returns:
        Injector: Configured injector instance.
    """
    return Injector([config.create_injector_builder(), configure])


def create_binder(cls: type[_T], ins: _T) -> Callable[[Binder], None]:
    """Create a binder function that binds a class to an instance."""

    def binder(binder: Binder) -> None:
        binder.bind(cls, to=ins)

    return binder
