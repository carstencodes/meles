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
from pathlib import Path
from typing import TYPE_CHECKING

from falcon import App  # type: ignore
from falcon.inspect import inspect_routes  # type: ignore
from falcon_caching import Cache  # type: ignore

from .core import (
    Generator,
    HasConfigItems,
    LogRecordingMiddleware,
    RequestHandler,
    RequestIDMiddleware,
    SharedCache,
    SupportsFalconGetRequest,
    SupportsResourceGeneration,
    Urllib3RequestHandler,
    config,
    setup_logger,
)
from .resources import (
    AllResources,
    HealthResource,
    PrometheusMiddleware,
    SystemResource,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Iterator


class _MelesApp(App):
    __resources: "list[SupportsFalconGetRequest]" = []
    __cache: "Cache" = SharedCache
    __generator_factory: "type[Generator]" = Generator
    __request_handler_factory: "type[RequestHandler]" = Urllib3RequestHandler

    @property
    def cache(self) -> "Cache":
        return self.__cache

    @cache.setter
    def cache(self, cache: "Cache") -> None:
        self.__cache = cache

    @property
    def request_handler_factory(self) -> "type[RequestHandler]":
        return self.__request_handler_factory

    @request_handler_factory.setter
    def request_handler_factory(
        self, request_handler_factory: "type[RequestHandler]"
    ) -> None:
        self.__request_handler_factory = request_handler_factory

    @property
    def generator_factory(self) -> "type[Generator]":
        return self.__generator_factory

    @generator_factory.setter
    def generator_factory(self, generator_factory: "type[Generator]") -> None:
        self.__generator_factory = generator_factory

    @property
    def resources(self) -> "Iterator[SupportsFalconGetRequest]":
        yield from self.__resources

    def add_family(self, family: "SupportsResourceGeneration") -> None:
        for resource in family.get_resources(
            self.cache, self.generator_factory, self.request_handler_factory
        ):
            self.add_resource(resource)

    def add_resource(self, resource: "SupportsFalconGetRequest") -> None:
        self.add_route(resource.route_template, resource)
        self.__resources.append(resource)


def get_app(
    cfg: "HasConfigItems" = config,
    cache: "Cache" = SharedCache,
    generator_factory: "type[Generator]" = Generator,
    request_handler_factory: "type[RequestHandler]" = Urllib3RequestHandler,
) -> _MelesApp:
    setup_logger(cfg.env.is_development)
    prom: "PrometheusMiddleware" = PrometheusMiddleware()
    app = _MelesApp(middleware=[RequestIDMiddleware(), LogRecordingMiddleware(), prom])
    app.cache = cache
    app.generator_factory = generator_factory
    app.request_handler_factory = request_handler_factory

    if not cfg.dynamic.setup(app):
        raise RuntimeError("Failed to configure Meles!")

    if cfg.env.is_development:
        app.add_route("/_all_routes", AllResources(list(app.resources)))

    if cfg.env.use_prometheus:
        app.add_route("/metrics", prom)

    if cfg.env.use_health_check:
        app.add_route("/health", HealthResource())

    def _get_routes():
        return inspect_routes(app)

    app.add_route("/system", SystemResource(_get_routes))

    res_folder: "Path" = Path(__file__).absolute().parent / "_res"

    app.add_static_route("/", res_folder)

    return app
