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
import importlib.metadata
import json
from typing import TYPE_CHECKING

import falcon  # type: ignore
import falcon_prometheus  # type: ignore
from prometheus_client import generate_latest  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, Iterable

    from falcon import Request, Response
    from falcon.inspect import RouteInfo  # type: ignore

    from ..core import SupportsFalconGetRequest


class AllResources:
    def __init__(self, resources: "list[SupportsFalconGetRequest]") -> None:
        self.__routes = [r.route_template for r in resources]

    def on_get(self, _: "Request", resp: "Response") -> None:
        resp.text = json.dumps(self.__routes)
        resp.status = falcon.HTTP_200
        resp.set_header("Content-Type", "application/json")


class SystemResource:
    def __init__(self, get_routes: "Callable[[], Iterable[RouteInfo]]") -> None:
        self.__get_routes = get_routes
        self.__routes: "list[RouteInfo]" = []
        self.__package = importlib.metadata.distribution("meles")

    def on_get(self, _: "Request", resp: "Response") -> None:
        if len(self.__routes) == 0:
            self.__routes = list(self.__get_routes())

        system = {
            "name": self.__package.name,
            "version": self.__package.version,
            "dependencies": self.__package.requires,
            "routes": [r.path for r in self.__routes],
            "license": self.__package.metadata.get("License", "n/a"),
            "urls": {
                k.split(",")[0].strip(): k.split(",")[1].strip()
                for k in self.__package.metadata.get_all("Project-URL", [])
                if "," in k
            },
        }

        resp.text = json.dumps(system)
        resp.status = falcon.HTTP_200
        resp.set_header("Content-Type", "application/json")


class HealthResource:
    def on_get(self, _: "Request", resp: "Response") -> None:
        resp.text = "OK"
        resp.status = falcon.HTTP_200
        resp.set_header("Content-Type", "text/plain")


class PrometheusMiddleware(falcon_prometheus.PrometheusMiddleware):
    def on_get(self, req, resp):
        data = generate_latest(self.registry)
        resp.content_type = "text/plain; version=0.0.4; charset=utf-8"
        resp.text = str(data.decode("utf-8"))
