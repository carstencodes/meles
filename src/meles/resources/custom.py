#
# Copyright (c) 2025 Carsten Igel.
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
from typing import TYPE_CHECKING, Any

from .base import BadgeRequestObject, BadgeResourceBase
from ..core import (
    BadgeData,
    Color,
    ProcessingError,
    Generator, 
    SharedCache, 
    Urllib3RequestHandler,
)


if TYPE_CHECKING:
    from falcon_caching import Cache  # type: ignore

    from ..core import RequestHandler, SupportsFalconGetRequest

    from ..core import Icon
    from ..source.custom.base import CustomBackendSource  # type: ignore


class CustomBackendBadgeResource(BadgeResourceBase):
    def __init__(self, 
                backends: "dict[str, CustomBackendSource]",
                cache: "Cache" = SharedCache,
                generator_class: "type[Generator]" = Generator,
                request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
        ) -> None:
        self.__backends = backends
    
    @property
    def route_template(self) -> str:
        return "/custom/backend/{backendName}"
    
    def _process_badge_request(self, request: "dict[str, Any]") -> "BadgeData":
        backend_name: str = request.get("backendName", None)
        if backend_name is None or backend_name not in self.__backends:
            raise ProcessingError(
                http.HTTPStatus.NOT_FOUND, f"Unknown backend: {backend_name}"
            )
        
        try:
            backend: "CustomBackendSource" = self.__backends[backend_name]
            label: str = backend.label
            color_name: "str | None" = request.get("color", None)
            color: "Color" = (
                Color.from_str(color_name)
                if color_name is not None
                else backend.default_color
            ) or backend.default_color
            icon: "Icon | None" = backend.icon

            text: str = backend.process(request)
            
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
