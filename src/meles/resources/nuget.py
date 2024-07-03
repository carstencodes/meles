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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..core import BadgeData, Generator, SharedCache, Urllib3RequestHandler
from ..sources.nuget import (
    LatestPackageDownloadsNugetV3Source,
    LatestPackageVersionNugetV3Source,
)
from .base import BadgeResourceBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from falcon_caching import Cache  # type: ignore

    from ..core import RequestHandler, UrlSourceBase
    from ..sources.nuget import NugetSourceBase


class NugetBadgeResourceBase(BadgeResourceBase, ABC):
    def __init__(
        self,
        src: "NugetSourceBase",
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
    ):
        super().__init__(cache, generator_class)
        self.__source = src

    def _process_badge_request(self, request: "dict[str, Any]") -> BadgeData:
        return self.__source.get_data(request, pre_lease=self._pre_releases_allowed)

    @property
    @abstractmethod
    def _pre_releases_allowed(self) -> "bool | None":
        ...


class LatestStablePackageVersionNugetBadgeResource(NugetBadgeResourceBase):
    def __init__(
        self,
        feed_url: "UrlSourceBase",
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ):
        super().__init__(
            LatestPackageVersionNugetV3Source(feed_url, request_handler_class),
            cache,
            generator_class,
        )

    @property
    def route_template(self) -> str:
        return "/nuget/v/{packageName}"

    @property
    def _pre_releases_allowed(self) -> "bool | None":
        return None


class LatestPreviewPackageVersionNugetBadgeResource(NugetBadgeResourceBase):
    def __init__(
        self,
        feed_url: "UrlSourceBase",
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ):
        super().__init__(
            LatestPackageVersionNugetV3Source(feed_url, request_handler_class),
            cache,
            generator_class,
        )

    @property
    def route_template(self) -> str:
        return "/nuget/vpre/{packageName}"

    @property
    def _pre_releases_allowed(self) -> "bool | None":
        return True


class PackageDownloadsNugetBadgeResource(NugetBadgeResourceBase):
    def __init__(
        self,
        feed_url: "UrlSourceBase",
        cache: "Cache" = SharedCache,
        generator_class: "type[Generator]" = Generator,
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ):
        super().__init__(
            LatestPackageDownloadsNugetV3Source(feed_url, request_handler_class),
            cache,
            generator_class,
        )

    @property
    def route_template(self) -> str:
        return "/nuget/dt/{packageName}"

    @property
    def _pre_releases_allowed(self) -> "bool | None":
        return None
