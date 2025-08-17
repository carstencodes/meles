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
from __future__ import annotations

import http
from abc import ABC, abstractmethod
from inspect import getmembers, isclass
from logging import Logger, getLogger
from pkgutil import iter_modules, ModuleInfo
from sys import modules
from types import ModuleType
from typing import TYPE_CHECKING, TypeVar, cast

from ..core import (
    LOGGER_NAME,
    Color,
    ProcessingError,
    Request,
    TemplateUrlSource,
    Urllib3RequestHandler,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from ..core import BadgeData, RequestHandler, UrlSourceBase


class SourceBase(ABC):
    def __init__(self) -> None:
        self.__logger = getLogger(LOGGER_NAME)

    @property
    def _logger(self) -> "Logger":
        return self.__logger

    @abstractmethod
    def get_data(self, data: "dict[str, Any]", **kwargs: "Any") -> "BadgeData":
        ...


class RequestSourceBase(SourceBase, ABC):
    def __init__(
        self, request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler
    ):
        super().__init__()
        self.__request_handler = request_handler_class()

    def _create_url(self, url: "UrlSourceBase", **kwargs: "Any") -> "UrlSourceBase":
        if isinstance(url, TemplateUrlSource):
            url.apply_context(kwargs)
        return url

    def _create_raw_request(self, url: "UrlSourceBase", **kwargs: "Any") -> "Request":
        url_data = url.to_url()
        return Request(url=url_data)

    @property
    def _request_handler(self) -> "RequestHandler":
        return self.__request_handler

    def _get_value_from_request(
        self, key: str, data: "dict[str, Any]", default: "Any"
    ) -> "Any":
        return default if key not in data else str(data[key])

    def _get_label_from_request(self, data: "dict[str, Any]", default: str) -> str:
        return default if "label" not in data else str(data["label"])

    def _get_color_from_request(
        self, data: "dict[str, Any]", default: "Color"
    ) -> "Color":
        color_value = data.get("color", None)
        if color_value is None:
            return default

        color = Color.from_str(str(color_value))
        if color is None:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, f"Invalid color: {color_value}"
            )

        return color


TInstance = TypeVar("TInstance")


class SourcesCollection:
    def __init__(self, module_ns: "ModuleType") -> "None":
        self.__module = module_ns

    def get_sources[T: TInstance](self, type_to_bind: "type") -> "dict[str, T]":  # type: ignore
        logger = getLogger(LOGGER_NAME)
        instances: "dict[str, T]" = {}  # type: ignore

        logger.debug("Searching module %s for child modules", self.__module.__name__)
        children: "list[ModuleInfo]" = list(
            iter_modules(
                self.__module.__path__,
                self.__module.__name__ + ".",
            )
        )

        for child in children:
            logger.debug("Found child module %s", child.name)
            if child.name not in modules:
                logger.warning("Failed to find child module %s", child.name)
                continue

            module = modules[child.name]
            for name, member in getmembers(module):
                logger.debug("Analyzing member %s", name)
                if isclass(member) and issubclass(member, type_to_bind):
                    logger.debug("Found matching type: %s", member.__name__)
                    clazz: "type[T]" = cast(type[T], member)  # type: ignore
                    try:
                        instance: "T" = clazz()  # type: ignore
                    except Exception as e:
                        logger.warning(
                            "Failed to instantiate class %s",
                            clazz.__qualname__,
                            exc_info=e,
                        )
                    
                    instance_name = member.__name__
                    if hasattr(instance, "name"):
                        instance_name = str(getattr(instance, "name"))

                    instances[instance_name] = instance

        return instances
