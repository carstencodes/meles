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

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from falcon_caching import Cache  # type: ignore

from ._config import config
from ._connect import RequestHandler, Urllib3RequestHandler
from ._generator import Generator

if TYPE_CHECKING:  # pragma: no cover
    from typing import Final, Iterator

    from falcon import Request, Response  # type: ignore


SharedCache: "Final[Cache]" = Cache(config.cache.get_options())


class SupportsFalconGetRequest(Protocol):
    @property
    def route_template(self) -> str:
        ...

    def on_get(self, req: "Request", resp: "Response") -> None:
        ...


class SupportsResourceGeneration(Protocol):
    def get_resources(
        self,
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_factory: "type[RequestHandler]" = Urllib3RequestHandler,
    ) -> "Iterator[SupportsFalconGetRequest]":
        ...


@runtime_checkable
class SupportsResources(Protocol):
    @property
    def cache(self) -> "Cache":
        ...

    @cache.setter
    def cache(self, cache: "Cache") -> None:
        ...

    @property
    def generator_factory(self) -> "type[Generator]":
        ...

    @generator_factory.setter
    def generator_factory(self, generator_factory: "type[Generator]") -> None:
        ...

    @property
    def request_handler_factory(self) -> "type[RequestHandler]":
        ...

    @request_handler_factory.setter
    def request_handler_factory(
        self, request_handler_factory: "type[RequestHandler]"
    ) -> None:
        ...

    @property
    def resources(self) -> "Iterator[SupportsFalconGetRequest]":
        ...

    def add_family(self, family: "SupportsResourceGeneration") -> None:
        ...

    def add_resource(self, resource: "SupportsFalconGetRequest") -> None:
        ...
