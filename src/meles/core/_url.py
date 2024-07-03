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
from string import Formatter
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlparse, urlunparse

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Mapping


class UrlSourceBase(ABC):
    @abstractmethod
    def get_url(self) -> str:
        ...

    def to_url(self) -> "Url":
        return Url(self)


class _StaticUrlSource(UrlSourceBase):
    def __init__(self, url: str):
        self.__url = url

    def get_url(self) -> str:
        return self.__url


class UrlBuilder(UrlSourceBase):
    def __init__(self, url: str) -> None:
        self.__parse_result = urlparse(url)
        self.__query = self.__parse_result.query

    def add_param(self, key: str, value: str) -> None:
        to_add = ""
        if len(self.__query) > 0:
            to_add = "&"
        to_add += f"{urlencode({key: value})}"
        if isinstance(self.__query, bytes):
            to_add = to_add.encode("utf-8")

        self.__query += to_add

    def build(self) -> "Url":
        return Url(self)

    def get_url(self) -> str:
        components = (
            self.__parse_result.scheme,
            self.__parse_result.netloc,
            self.__parse_result.path,
            self.__parse_result.params,
            self.__query,
            self.__parse_result.fragment,
        )
        return str(urlunparse(components))


class TemplateUrlSource(UrlSourceBase):
    def __init__(self, url_template: str) -> None:
        self.__url_template = url_template
        self.__vars: "dict[str, str | None]" = {}
        self.__var_names: "list[str]" = []
        for f in Formatter().parse(url_template):
            _, name, _, _ = f
            if name is not None:
                self.__var_names.append(name)

    def apply_context(self, context: "Mapping[str, str]") -> None:
        for s in self.__var_names:
            if s in context:
                self.__vars[s] = context[s]

    def apply(self, **kwargs: "Any") -> None:
        self.apply_context(kwargs)

    def get_url(self) -> str:
        remaining = [k for k in self.__var_names if k not in self.__vars]
        if len(remaining) > 0:
            raise ValueError(f"Missing variables: {', '.join(remaining)}")

        return self.__url_template.format(**self.__vars)


class Url:
    def __init__(self, src: "UrlSourceBase") -> None:
        self.__src = src

    def __str__(self) -> str:
        return self.__src.get_url()

    def __repr__(self) -> str:
        return f"class<{self.__class__.__name__}>({repr(self.__src)})"

    @property
    def source(self) -> "UrlSourceBase":
        return self.__src

    @staticmethod
    def static(url: str) -> "Url":
        src = _StaticUrlSource(url)
        return Url(src)
