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

import pytest
from falcon_caching import Cache
from meles.core import Generator
from meles.app import get_app
from ._mocks import TestConfig, TestEnvConfig, TestCacheConfig, TestDynamicConfig, TestRequestHandler


@pytest.fixture
def use_prometheus():
    return True


@pytest.fixture
def use_health_check():
    return True


@pytest.fixture
def env_config(use_prometheus, use_health_check):
    return TestEnvConfig(use_prometheus, use_health_check)


@pytest.fixture
def cache_options():
    return {}


@pytest.fixture
def cache_config(cache_options):
    return TestCacheConfig(cache_options)


@pytest.fixture
def setup_successful():
    return True


@pytest.fixture
def dynamic_config(setup_successful):
    return TestDynamicConfig(setup_successful)


@pytest.fixture
def config(env_config, cache_config, dynamic_config):
    return TestConfig(env_config, cache_config, dynamic_config)


@pytest.fixture
def falcon_cache():
    return Cache(config={
        "CACHE_TYPE": "null",
    })


@pytest.fixture
def generator_type():
    return Generator


@pytest.fixture
def request_handler_type():
    return TestRequestHandler


@pytest.fixture
def app(config, falcon_cache, generator_type, request_handler_type):
    return get_app(config, falcon_cache, generator_type, request_handler_type)
