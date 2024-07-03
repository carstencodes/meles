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
import json
import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

import falcon  # type: ignore
from falcon_caching import Cache  # type: ignore

from ..core import (
    LOGGER_NAME,
    BadgeData,
    Color,
    ColorValues,
    Generator,
    Icons,
    ProcessingError,
    SharedCache,
    config,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Final, Mapping

    from falcon import Request, Response  # type: ignore

    from ..core import SupportsFalconGetRequest


class BadgeResourceBase(ABC):
    def __init__(
        self,
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
    ):
        self.__generator = generator_class()
        self.__logger = logging.getLogger(LOGGER_NAME)
        self.__cache = cache

    @property
    @abstractmethod
    def route_template(self) -> str:
        ...

    @property
    def _logger(self) -> "logging.Logger":
        return self.__logger

    def on_get(self, req: "Request", resp: "Response", **kwargs: "Any") -> None:
        try:
            reply: str
            query: "dict[str, Any]" = req.params
            cache_key: str = self.__get_cache_key(req.path, query)
            if self.__cache.has(cache_key):
                self.__logger.info(
                    "Processing request '%s' from cache using cache key '%s'",
                    req.url,
                    cache_key,
                )
                reply = self.__cache.get(cache_key)
            else:
                self.__logger.info(
                    "Processing request '%s' as new request using cache key '%s'",
                    req.url,
                    cache_key,
                )
                reply = self.__generate_badge_from_request(cache_key, req, **kwargs)

            resp.text = reply
            resp.status = falcon.HTTP_200
            resp.set_header("Content-Type", "image/xvg+xml")
        except Exception as exc:  # pylint: disable=W0703
            self.__logger.exception(
                "Failed to process request '%s'", req.url, exc_info=exc
            )
            resp.status = falcon.HTTP_500
            if isinstance(exc, ProcessingError):
                trace_back = traceback.format_exception(exc)
                processing_error = cast("ProcessingError", exc)
                resp.status = falcon.code_to_http_status(processing_error.status_code)
                resp.text = processing_error.message + "\n" + "\n".join(trace_back)
                resp.set_header("Content-Type", "text/plain")

    def __generate_badge_from_request(
        self, cache_key: str, req: "Request", **kwargs: "Any"
    ) -> str:
        document: "dict[str, Any]" = {}
        headers: "dict[str, Any]" = req.headers
        query: "dict[str, Any]" = req.params
        if "cacheSeconds" in query:
            timeout = int(query.pop("cacheSeconds"))
        else:
            timeout = None
        data: "dict[str, Any]" = {}
        data.update(headers)
        data.update(query)
        data.update(document)
        data.update(kwargs)
        badge: BadgeData = self._process_badge_request(data)
        self.__logger.debug("Will try to generate te following badge: %s", badge)
        reply: str = self.__generator.transform(badge)
        self.__cache.set(cache_key, reply, timeout=timeout)
        return reply

    @abstractmethod
    def _process_badge_request(self, request: "dict[str, Any]") -> BadgeData:
        ...

    def __get_cache_key(self, path: str, query: "Mapping[str, str]") -> str:
        clazz: str = self.__class__.__name__
        q_string: str = ";".join([f"{k}={v}" for k, v in query.items()])

        return f"{clazz}:{path}:{q_string}"


@dataclass
class BadgeRequestObject:
    logo: "str | None" = field(default=None)
    logo_color: "str | None" = field(default=None)
    label: "str | None" = field(default=None)
    color: "str | None" = field(default=None)
    cache_seconds: "int | None" = field(default=None)
    style: "str | None" = field(default=None)
    message: "str | None" = field(default=None)

    @staticmethod
    def parse(data: "dict[str, Any]") -> "BadgeRequestObject":
        return BadgeRequestObject(
            logo=data.get("logo"),
            logo_color=data.get("logoColor"),
            label=data.get("label"),
            color=data.get("color"),
            cache_seconds=int(str(data.get("cacheSeconds") or "")),
            style=data.get("style"),
            message=data.get("message"),
        )

    def to_badge(self, **kwargs: "Any") -> "BadgeData":
        logo_color = (
            Color.from_str(self.logo_color)
            if self.logo_color is not None
            else ColorValues.LIGHT_GREY.value
        ) or ColorValues.LIGHT_GREY.value

        data = {
            "label": self.label or "<undefined>",
            "text": self.message or "<undefined>",
            "color": Color.from_str(self.color)
            if self.color is not None
            else ColorValues.GREEN.value,
            "icon": Icons.custom(self.logo, logo_color)
            if self.logo is not None
            else None,
        }

        for key in kwargs.keys():
            if key in data:
                data[key] = kwargs[key]

        return BadgeData(**data)  # type: ignore
