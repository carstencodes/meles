#
# Copyright (c) 2024 Carsten Igel.
#
# This file is part of meles
# (see https://github.com/carstencodes/meles).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import pkgutil
from functools import cached_property
from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, Iterator, Mapping

    from ._falcon import SupportsResources


class _Environment:
    def __init__(self) -> None:
        self.__name = os.environ.get("MELES_ENVIRONMENT", "PRODUCTION")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_production(self) -> bool:
        return self.name.upper() == "PRODUCTION"

    @property
    def is_development(self) -> bool:
        return self.name.upper() == "DEVELOPMENT"

    @property
    def use_prometheus(self) -> bool:
        return bool(os.environ.get("MELES_USE_PROMETHEUS", "True"))

    @property
    def use_health_check(self) -> bool:
        return bool(os.environ.get("MELES_USE_HEALTHCHECK", "True"))


class _ProvidesEnvConfig(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def is_production(self) -> bool:
        ...

    @property
    def is_development(self) -> bool:
        ...

    @property
    def use_prometheus(self) -> bool:
        ...

    @property
    def use_health_check(self) -> bool:
        ...


class _CacheConfig:
    def __init__(self) -> None:
        self.__options: "Mapping[str, str]" = {}
        for key, value in os.environ.items():
            if key.upper().startswith("MELES_CACHE_"):
                new_key = key.replace("MELES_", "")
                self.__options[new_key] = value

        if "CACHE_TYPE" not in self.__options:
            self.__options["CACHE_TYPE"] = "simple"

    def get_options(self) -> "Mapping[str, str]":
        return self.__options


class _ProvidesCacheConfig(Protocol):
    def get_options(self) -> "Mapping[str, str]":
        ...


class _DynamicConfig:
    @cached_property
    def _configurators(self) -> "list[Callable[[SupportsResources], None]]":
        return list(_DynamicConfig.__get_configurators())

    def setup(self, app: "SupportsResources") -> bool:
        if len(self._configurators) == 0:
            return False

        for configurator in self._configurators:
            configurator(app)

        return True

    @staticmethod
    def __get_configurators() -> "Iterator[Callable[[SupportsResources], None]]":
        configurator_module: "Callable[[SupportsResources], None] | None" = (
            _DynamicConfig.__get_configurator_module()
        )
        if configurator_module is not None:
            yield configurator_module

        for ep in entry_points(group="meles.configure"):
            loaded_ep = ep.load()
            if callable(loaded_ep):
                yield loaded_ep

    @staticmethod
    def __get_configurator_module() -> "Callable[[SupportsResources], None] | None":
        module_and_attr_name = os.getenv(
            "MELES_CONFIGURATION_MODULE", "meles.default:configure"
        )
        if module_and_attr_name is not None:
            attr = pkgutil.resolve_name(module_and_attr_name)
            if attr is not None and callable(attr):
                return attr

        return None


class _SupportsDynamicConfig(Protocol):
    def setup(self, app: "SupportsResources") -> bool:
        ...


class _RuntimeConfig:
    def __init__(self) -> None:
        self.__env = _Environment()
        self.__cache = _CacheConfig()
        self.__dynamic = _DynamicConfig()

    @property
    def env(self) -> _Environment:
        return self.__env

    @property
    def dynamic(self) -> _DynamicConfig:
        return self.__dynamic

    @property
    def host(self) -> "str | None":
        return os.environ.get("MELES_HOST") or (
            "127.0.0.1" if self.__env.is_development else "0.0.0.0"
        )

    @property
    def port(self) -> "int | None":
        port: "str | None" = os.environ.get("MELES_PORT")
        if port is None:
            return 8080

        if not port.isdigit():
            return None

        return int(port)

    @property
    def cache(self) -> "_CacheConfig":
        return self.__cache


class HasConfigItems(Protocol):
    @property
    def env(self) -> _ProvidesEnvConfig:
        ...

    @property
    def dynamic(self) -> _SupportsDynamicConfig:
        ...

    @property
    def host(self) -> "str | None":
        ...

    @property
    def port(self) -> "int | None":
        ...

    @property
    def cache(self) -> "_ProvidesCacheConfig":
        ...


config: "HasConfigItems" = _RuntimeConfig()
