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

from typing import TYPE_CHECKING

from ..core import Generator, SharedCache, Urllib3RequestHandler
from ..resources.custom import CustomBackendBadgeResource
from .base import FamilyBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterator

    from falcon_caching import Cache  # type: ignore

    from ..core import RequestHandler, SupportsFalconGetRequest

    from ..sources.custom.base import CustomBackendSource


class CustomFamily(FamilyBase):
    def __init__(self, backends: "dict[str, CustomBackendSource]") -> None:
        self.__backends = backends
    

    def get_resources(
        self,
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ) -> "Iterator[SupportsFalconGetRequest]":
        yield CustomBackendBadgeResource(self.__backends, cache, generator_class, request_handler_class)
