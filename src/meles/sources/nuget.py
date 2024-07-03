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
from dataclasses import dataclass, field
from http import HTTPStatus
from json import loads as load_json
from random import choice as random_choice
from typing import TYPE_CHECKING

from semver import Version

from ..core import (
    BadgeData,
    ColorValues,
    Icons,
    ProcessingError,
    Request,
    Response,
    Url,
    UrlBuilder,
    Urllib3RequestHandler,
)
from .base import RequestSourceBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from ..core import UrlSourceBase
    from .base import RequestHandler


class NugetSourceBase(RequestSourceBase, ABC):
    def __init__(
        self,
        feed_url: "UrlSourceBase",
        request_handler_class: "type[RequestHandler]" = Urllib3RequestHandler,
    ):
        super().__init__(request_handler_class)
        self.__feed_url = feed_url

    @property
    def feed_url(self) -> "UrlSourceBase":
        return self.__feed_url

    def get_data(self, data: "dict[str, Any]", **kwargs: "Any") -> "BadgeData":
        req: "Request" = self._create_request(data, **kwargs)
        resp: "Response" = self._request_handler.handle_request(req)

        return self._create_badge(resp, data)

    @abstractmethod
    def _create_request(self, data: "dict[str, Any]", **kwargs: "Any") -> "Request":
        ...

    @abstractmethod
    def _create_badge(
        self, resp: "Response", data: "dict[str, Any]", **kwargs: "Any"
    ) -> "BadgeData":
        ...


class NugetV3Source(NugetSourceBase, ABC):
    def _create_request(self, data: "dict[str, Any]", **kwargs: "Any") -> "Request":
        url: "Url" = self._create_url(self.feed_url, **data).to_url()
        search_service_url: str = self._select_search_service(url)
        builder: UrlBuilder = UrlBuilder(search_service_url)

        package_name = self._get_value_from_request("packageName", data, None)
        if package_name is None:
            raise ProcessingError(
                HTTPStatus.BAD_REQUEST,
                "'packageName' property is missing",
            )

        builder.add_param("q", package_name)

        pre_release = kwargs.pop("pre_release", None)

        if pre_release is not None:
            builder.add_param("prerelease", str(bool(pre_release)))

        req: Request = self._create_raw_request(
            url=builder,
            **data,
        )

        return req

    def _select_search_service(self, url: "Url") -> str:
        self._logger.debug("Selecting search service from %s", url)
        response = self._request_handler.handle_request(Request(url))
        json_response: "dict[str, Any]" = (
            load_json(response.data.decode("utf-8"))
            if response.data is not None
            else {}
        )
        if "resources" not in json_response:
            raise ProcessingError(
                HTTPStatus.SERVICE_UNAVAILABLE,
                f"{self.feed_url} did not provide any resources",
            )

        candidates = set()
        for resource in json_response["resources"]:
            if (
                "@type" in resource
                and "@id" in resource
                and str(resource["@type"])
                .lower()
                .startswith("SearchQueryService".lower())
            ):
                candidates.add(resource["@id"])

        if len(candidates) == 0:
            raise ProcessingError(
                HTTPStatus.SERVICE_UNAVAILABLE,
                f"{self.feed_url} did not provide any search query services",
            )

        self._logger.debug(
            "Found %i distinct search services. Choosing one arbitrarily",
            len(candidates),
        )

        return random_choice(list(candidates))

    @property
    def default_label(self) -> str:
        return "nuget"

    def _create_badge(
        self, resp: "Response", data: "dict[str, Any]", **kwargs: "Any"
    ) -> "BadgeData":
        pkg: "NuGetPackage | None" = self._filter_nuget_package(resp, data)
        if pkg is None:
            raise ProcessingError(
                HTTPStatus.NOT_FOUND, f"Failed to resolve {resp.url}: NOT FOUND"
            )

        text = self._select_text(pkg)
        label = self._get_label_from_request(data, self.default_label)
        color = self._get_color_from_request(data, ColorValues.GREEN.value)

        return BadgeData(
            icon=Icons.NUGET.value,
            label=label,
            text=text,
            color=color,
        )

    @abstractmethod
    def _filter_nuget_package(
        self, response: "Response", data: "dict[str, Any]"
    ) -> "NuGetPackage | None":
        ...

    @abstractmethod
    def _select_text(self, package: "NuGetPackage") -> str:
        ...

    def _parse_nuget_v3_search_response(
        self, response: "Response"
    ) -> "NuGetV3SearchResponse | None":
        json_data = response.data.decode("utf-8") if response.data is not None else ""
        json_object = load_json(json_data)

        return NuGetV3SearchResponse.parse(json_object)


class LatestPackageNugetV3Source(NugetV3Source, ABC):
    def _filter_nuget_package(
        self, response: "Response", data: "dict[str, Any]"
    ) -> "NuGetPackage | None":
        search_response = self._parse_nuget_v3_search_response(response)
        if search_response is None:
            raise ProcessingError(
                HTTPStatus.EXPECTATION_FAILED,
                f"Failed to parse response of {response.url}",
            )

        name = str(self._get_value_from_request("packageName", data, ""))

        major = int(self._get_value_from_request("major", data, -1))
        minor = int(self._get_value_from_request("minor", data, -1))

        versions = []
        for pkg in search_response.data:
            if pkg.id == name:
                for pkg_version in pkg.versions:
                    try:
                        versions.append(
                            (
                                name,
                                Version.parse(pkg_version.version),
                                pkg_version.downloads,
                            )
                        )
                    except (ValueError, TypeError):
                        continue

        if major >= 0:
            versions = [
                v
                for v in versions
                if v[1].major == major and (minor < 0 or v[1].minor == minor)
            ]

        if len(versions) == 0:
            raise ProcessingError(
                HTTPStatus.BAD_REQUEST, f"Failed to resolve package data for {name}"
            )

        max_version = max(*versions, key=lambda v: v[1])
        return NuGetPackage(max_version[0], str(max_version[1]), max_version[2])


class LatestPackageVersionNugetV3Source(LatestPackageNugetV3Source):
    def _select_text(self, package: "NuGetPackage") -> str:
        return package.version


class LatestPackageDownloadsNugetV3Source(LatestPackageNugetV3Source):
    @property
    def default_label(self) -> str:
        return "downloads"

    def _select_text(self, package: "NuGetPackage") -> str:
        return str(package.downloads)


class NuGetPackage:
    name: str
    version: str
    downloads: int

    def __init__(self, name: str, version: str, downloads: int) -> None:
        self.name = name
        self.version = version
        self.downloads = downloads


@dataclass
class NuGetV3PackageType:
    name: str

    @staticmethod
    def parse(data: "dict[str, Any]") -> "NuGetV3PackageType":
        return NuGetV3PackageType(data["name"])


@dataclass
class NuGetV3Version:
    id: str  # pylint: disable=C0103
    version: str
    downloads: int

    @staticmethod
    def parse(data: "dict[str, Any]") -> "NuGetV3Version":
        return NuGetV3Version(data["@id"], data["version"], int(data["downloads"]))


@dataclass
class NuGetV3SearchResult:  # pylint: disable=R0902
    id: str = field()  # pylint: disable=C0103
    version: str = field()
    versions: list[NuGetV3Version] = field(default_factory=list)
    package_types: "list[NuGetV3PackageType]" = field(default_factory=list)
    description: "str | None" = field(default=None)
    authors: "str | list[str] | None" = field(default=None)
    icon_url: "str | None" = field(default=None)
    license_url: "str | None" = field(default=None)
    owners: "str | list[str] | None" = field(default=None)
    project_url: "str | None" = field(default=None)
    registration: "str | None" = field(default=None)
    summary: "str | None" = field(default=None)
    tags: "str | list[str] | None" = field(default=None)
    title: "str | None" = field(default=None)
    total_downloads: "int | None" = field(default=None)
    verified: "bool | None" = field(default=None)

    @staticmethod
    def parse(data: "dict[str, Any]") -> "NuGetV3SearchResult":

        return NuGetV3SearchResult(
            data["id"],
            data["version"],
            [NuGetV3Version.parse(d) for d in data.get("versions", [])],
            [NuGetV3PackageType.parse(d) for d in data.get("packageTypes", [])],
        )


@dataclass
class NuGetV3SearchResponse:
    total_hits: int = field(default=0)
    data: list[NuGetV3SearchResult] = field(default_factory=list)

    @staticmethod
    def parse(data: "dict[str, Any]") -> "NuGetV3SearchResponse | None":
        try:
            return NuGetV3SearchResponse(
                int(data["totalHits"]),
                [NuGetV3SearchResult.parse(d) for d in data.get("data", [])],
            )
        except Exception as exc:
            raise ProcessingError(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                "Failed to parse NuGet v3 search response",
            ) from exc
