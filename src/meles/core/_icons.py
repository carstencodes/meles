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
from base64 import b64encode
from enum import Enum

from simpleicons.all import icons  # type: ignore
from simpleicons.icon import Icon as SimpleIcon  # type: ignore
from simpleicons.icons import si_nuget as nuget_logo  # type: ignore

from ._color import Color, ColorValues


class Icon(ABC):
    def __init__(self, color: "Color" = ColorValues.LIGHT_GREY.value):
        self.__color = color

    @property
    def color(self) -> Color:
        return self.__color

    @abstractmethod
    def build_svg(self) -> bytes:
        ...

    def encode_as_data_url(self) -> str:
        xml: bytes = self.build_svg()
        base64_xml = b64encode(xml).decode("utf-8")
        return f"data:image/svg+xml;base64, {base64_xml}"


class _SimpleIcon(Icon):
    def __init__(
        self, source_icon: "SimpleIcon", color: "Color" = ColorValues.LIGHT_GREY.value
    ) -> None:
        super().__init__(color)
        self.__source_icon = source_icon

    def build_svg(self) -> bytes:
        return self.__source_icon.get_xml_bytes(fill=self.color.to_rgb_hex_color())


class _NugetIcon(_SimpleIcon):
    def __init__(self) -> None:
        super().__init__(nuget_logo, Color.from_hex_assured("#004681"))


class Icons(Enum):
    NUGET = _NugetIcon()

    @staticmethod
    def custom(name: str, color: "Color" = ColorValues.LIGHT_GREY.value) -> "Icon":
        icon: "SimpleIcon" = icons.get(name)

        if icon is None:
            raise ValueError(f"'{name}' is not a valid icon")

        return _SimpleIcon(icon, color)
