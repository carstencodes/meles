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
from logging import Logger, getLogger
from typing import TYPE_CHECKING

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
