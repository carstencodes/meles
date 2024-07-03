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

from meles.core import RequestHandler, Generator, Request, Response


class TestRequestHandler(RequestHandler):
    def handle_request(self, request: "Request") -> "Response":
        raise NotImplementedError()


class TestDynamicConfig:
    def __init__(self, setup_successful):
        self.__setup_successful = setup_successful

    def setup(self, _):
        return self.__setup_successful


class TestCacheConfig:
    def __init__(self, cache_options):
        self.__cache_opts = cache_options

    def get_options(self):
        return self.__cache_opts


class TestEnvConfig:
    def __init__(self, use_prometheus, use_health_check):
        self.__use_prometheus = use_prometheus
        self.__use_health_check = use_health_check

    @property
    def name(self) -> str:
        return "PYTEST"

    @property
    def is_production(self) -> bool:
        return False

    @property
    def is_development(self) -> bool:
        return True

    @property
    def use_prometheus(self) -> bool:
        return self.__use_prometheus

    @property
    def use_health_check(self) -> bool:
        return self.__use_health_check


class TestConfig:
    def __init__(self, env_config: TestEnvConfig, cache_config: TestCacheConfig, dynamic_config: TestDynamicConfig):
        self.__env_config = env_config
        self.__cache_config = cache_config
        self.__dynamic_config = dynamic_config

    @property
    def env(self):
        return self.__env_config

    @property
    def dynamic(self):
        return self.__dynamic_config

    @property
    def host(self) -> "str | None":
        return None

    @property
    def port(self) -> "int | None":
        return None

    @property
    def cache(self):
        return self.__cache_config


__all__ = ["TestRequestHandler", "TestDynamicConfig", "TestCacheConfig", "TestEnvConfig", "TestConfig"]
