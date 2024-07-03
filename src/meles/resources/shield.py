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
import http
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import BytesIO
from json import loads as load_json
from tomllib import loads as load_toml
from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element, ElementTree
from xml.etree.ElementTree import tostring as xml_to_string

from jsonpath import jsonpath  # type: ignore
from yaml import safe_load as load_yaml

from ..core import (
    BadgeData,
    Color,
    ColorValues,
    Generator,
    Icons,
    ProcessingError,
    Request,
    SharedCache,
    Urllib3RequestHandler,
)
from .base import BadgeRequestObject, BadgeResourceBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from falcon_caching import Cache  # type: ignore

    from ..core import Icon, RequestHandler, Response


class ShieldResource(BadgeResourceBase):
    @property
    def route_template(self) -> str:
        return "/badge/{badgeContent}"

    def _process_badge_request(self, request: "dict[str, Any]") -> "BadgeData":
        try:
            text: str = ShieldResource.__parse_text(request.get("badgeContent"))
            label: str = ShieldResource.__parse_text(request.get("label", "shield"))
            color_name: "str | None" = request.get("color")
            color: "Color" = (
                Color.from_str(color_name)
                if color_name is not None
                else ColorValues.GREEN.value
            ) or ColorValues.GREEN.value
            icon_name: "str | None" = request.get("icon", None)
            icon: "Icon | None" = None
            if icon_name is not None:
                icon_color: "str | None" = request.get("logoColor")
                icon = (
                    Icons.custom(icon_name)
                    if icon_color is None
                    else Icons.custom(
                        icon_name,
                        Color.from_str(icon_color) or ColorValues.LIGHT_GREY.value,
                    )
                )

            return BadgeData(
                label=label,
                color=color,
                text=text,
                icon=icon,
            )
        except Exception as exc:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, "Failed to process shield request"
            ) from exc

    @staticmethod
    def __parse_text(text: "str | None") -> str:
        return (
            (text or "")
            .replace("%20", " ")
            .replace("_", " ")
            .replace("__", "_")
            .replace("--", "-")
        )


class _CustomSourceBase(BadgeResourceBase, ABC):
    def __init__(
        self,
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ) -> None:
        super().__init__(cache, generator_class)
        self.__request_handler = request_handler_class()

    def _process_badge_request(self, request: "dict[str, Any]") -> "BadgeData":
        if "url" not in request:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, "Url parameter is missing"
            )

        url = request["url"]
        req: "Request" = Request(url=url)
        response = self.__request_handler.handle_request(req)

        if response.status != http.HTTPStatus.OK:
            raise ProcessingError(
                http.HTTPStatus.BAD_GATEWAY,
                f"Failed to call {url}. Result {response.status}",
            )

        return self._process_invocation_result(response, request)

    @abstractmethod
    def _process_invocation_result(
        self, response: "Response", request_data: "dict[str, Any]"
    ) -> "BadgeData":
        ...


@dataclass
class _EndPointData:
    label: str = field()
    message: str = field()
    color: str = field(default="lightgrey")
    label_color: str = field(default="grey")
    is_error: bool = field(default=False)
    named_logo: "str | None" = field(default=None)
    logo_color: "str | None" = field(default=None)

    @staticmethod
    def parse(values: "dict[str, Any]") -> "_EndPointData":
        return _EndPointData(
            values["label"],
            values["message"],
            str(values.get("color") or ""),
            str(values.get("labelColor") or ""),
            bool(values.get("isError", "False")),
            values.get("namedLogo"),
            values.get("logoColor"),
        )


class EndpointResource(_CustomSourceBase):
    @property
    def route_template(self) -> str:
        return "/endpoint"

    def _process_invocation_result(
        self, response: "Response", request_data: "dict[str, Any]"
    ) -> "BadgeData":
        if (
            response.has_header("Content-Type")
            and response.get_header("Content-Type") != "application/json"
        ):
            raise ProcessingError(
                http.HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Content type is not JSON"
            )

        if response.data is None:
            raise ProcessingError(
                http.HTTPStatus.SERVICE_UNAVAILABLE, "Requested yielded no data"
            )

        data = load_json(response.data)
        if "schemaVersion" not in data or data["schemaVersion"] != "1":
            raise ProcessingError(
                http.HTTPStatus.UNPROCESSABLE_ENTITY,
                "Expected a JSON object with 'schemaVersion': 1",
            )

        end_point: _EndPointData = _EndPointData.parse(data)

        logo_color = (
            Color.from_str(end_point.logo_color)
            if end_point.logo_color is not None
            else ColorValues.LIGHT_GREY.value
        )

        return BadgeData(
            label=end_point.label,
            color=Color.from_str(end_point.color) or ColorValues.GREEN.value,
            text=end_point.message,
            icon=(
                Icons.custom(
                    end_point.named_logo,
                    logo_color or ColorValues.LIGHT_GREY.value,
                )
                if end_point.named_logo is not None
                else None
            ),
        )


class DynamicBadgeResourceBase(_CustomSourceBase, ABC):
    @property
    def route_template(self) -> str:
        return f"/dynamic/{self.data_format}"

    @property
    @abstractmethod
    def data_format(self) -> str:
        ...

    @property
    @abstractmethod
    def content_types(self) -> tuple[str, ...]:
        ...

    def _process_invocation_result(
        self, response: "Response", request_data: "dict[str, Any]"
    ) -> "BadgeData":
        if (
            response.has_header("Content-Type")
            and response.get_header("Content-Type") not in self.content_types
        ):
            raise ProcessingError(
                http.HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                f"Expected content type: {self.content_types}",
            )

        if response.data is None:
            raise ProcessingError(
                http.HTTPStatus.SERVICE_UNAVAILABLE, "Requested yielded no data"
            )

        data = self._load_data(response.data)
        query = request_data.get("query")
        if query is None:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, "Missing parameter 'query'"
            )

        message = self._query_data(data, query)
        prefix = data.get("prefix", "")
        suffix = data.get("suffix", "")
        message = f"{prefix}{message}{suffix}"

        badge_elements = BadgeRequestObject.parse(data)

        return badge_elements.to_badge(text=message)

    @abstractmethod
    def _load_data(self, data: bytes) -> "dict[str, Any]":
        ...

    @abstractmethod
    def _query_data(self, data: "dict[str, Any]", query: str) -> str:
        ...


class DynamicJsonBadgeResource(DynamicBadgeResourceBase):
    @property
    def data_format(self) -> str:
        return "json"

    @property
    def content_types(self) -> tuple[str, ...]:
        return "application/json", "text/json"

    def _load_data(self, data: bytes) -> "dict[str, Any]":
        return load_json(data)

    def _query_data(self, data: "dict[str, Any]", query: str) -> str:
        value = jsonpath(data, query, "VALUE")
        if value is None:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, f"Failed to evaluate '{query}' in response"
            )

        return str(value)


class DynamicYamlBadgeResource(DynamicBadgeResourceBase):
    @property
    def data_format(self) -> str:
        return "yaml"

    @property
    def content_types(self) -> tuple[str, ...]:
        return "application/x-yaml", "text/yaml"

    def _load_data(self, data: bytes) -> "dict[str, Any]":
        return load_yaml(data)

    def _query_data(self, data: "dict[str, Any]", query: str) -> str:
        value = jsonpath(data, query, "VALUE")
        if value is None:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, f"Failed to evaluate '{query}' in response"
            )

        return str(value)


class DynamicTomlBadgeResource(DynamicBadgeResourceBase):
    @property
    def data_format(self) -> str:
        return "toml"

    @property
    def content_types(self) -> tuple[str, ...]:
        return ("application/toml",)

    def _load_data(self, data: bytes) -> "dict[str, Any]":
        return load_toml(data.decode("utf-8"), parse_float=float)

    def _query_data(self, data: "dict[str, Any]", query: str) -> str:
        value = jsonpath(data, query, "VALUE")
        if value is None:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, f"Failed to evaluate '{query}' in response"
            )

        return str(value)


class DynamicXmlBadgeResource(DynamicBadgeResourceBase):
    @property
    def data_format(self) -> str:
        return "xml"

    @property
    def content_types(self) -> tuple[str, ...]:
        return ("text/xml",)

    def _load_data(self, data: bytes) -> "dict[str, Any]":
        return {"__data__": ElementTree().parse(source=BytesIO(data), parser=None)}

    def _query_data(self, data: "dict[str, Any]", query: str) -> str:
        tree: "ElementTree" = data["__data__"]
        result = tree.findall(query)
        if len(result) == 0:
            raise ProcessingError(
                http.HTTPStatus.BAD_REQUEST, f"Failed to evaluate '{query}' in response"
            )

        result_data = ""
        for element in result:
            if isinstance(element, Element):
                result_data += xml_to_string(element, encoding="unicode")
            elif isinstance(element, str):
                result_data += element

        return result_data
