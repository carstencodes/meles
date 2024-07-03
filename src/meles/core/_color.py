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

from dataclasses import dataclass, field
from enum import Enum
from re import compile as re_compile
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from re import Match, Pattern
    from typing import Final


hex_parse: "Final[Pattern[str]]" = re_compile(r"[0-9a-fA-F]{2}")


@dataclass(frozen=True)
class Color:
    red_part: int = field(default=0)
    green_part: int = field(default=0)
    blue_part: int = field(default=0)

    @staticmethod
    def from_hex(hex_value: str) -> "Color | None":
        parse_result: "list[Match[str]]" = hex_parse.findall(hex_value)
        if parse_result is None or len(parse_result) != 3:
            return None

        _red, _green, _blue = tuple(parse_result)
        r_parsed = int(str(_red), 16)
        g_parsed = int(str(_green), 16)
        b_parsed = int(str(_blue), 16)

        return Color(red_part=r_parsed, green_part=g_parsed, blue_part=b_parsed)

    @staticmethod
    def from_hex_assured(hex_value: str) -> "Color":
        value = Color.from_hex(hex_value)
        if value is None:
            raise ValueError("hex value cannot be parsed")

        return value

    @staticmethod
    def from_name(name: str) -> "Color | None":
        name = name.lower()
        if name not in all_color_names:
            return None

        return ColorValues[name].value

    @staticmethod
    def from_str(value: str) -> "Color | None":
        return Color.from_hex(value) or Color.from_name(value)

    def to_hex(self) -> str:
        return bytearray([self.red_part, self.green_part, self.blue_part]).hex()

    def to_rgb_hex_color(self) -> str:
        return f"#{self.to_hex()}"


class ColorValues(Enum):
    ALICE_BLUE = Color.from_hex_assured("F0F8FF")
    ANTIQUE_WHITE = Color.from_hex_assured("FAEBD7")
    AQUA = Color.from_hex_assured("00FFFF")
    AQUA_MARINE = Color.from_hex_assured("7FFFD4")
    AZURE = Color.from_hex_assured("F0FFFF")
    BEIGE = Color.from_hex_assured("F5F5DC")
    BISQUE = Color.from_hex_assured("FFE4C4")
    BLACK = Color.from_hex_assured("000000")
    BLANCHED_ALMOND = Color.from_hex_assured("FFEBCD")
    BLUE = Color.from_hex_assured("0000FF")
    BLUE_VIOLET = Color.from_hex_assured("8A2BE2")
    BROWN = Color.from_hex_assured("A52A2A")
    BURLY_WOOD = Color.from_hex_assured("DEB887")
    CADET_BLUE = Color.from_hex_assured("5F9EA0")
    CHARTREUSE = Color.from_hex_assured("7FFF00")
    CHOCOLATE = Color.from_hex_assured("D2691E")
    CORAL = Color.from_hex_assured("FF7F50")
    CORNFLOWER_BLUE = Color.from_hex_assured("6495ED")
    CORNSILK = Color.from_hex_assured("FFF8DC")
    CRIMSON = Color.from_hex_assured("DC143C")
    CYAN = Color.from_hex_assured("00FFFF")
    DARK_BLUE = Color.from_hex_assured("00008B")
    DARK_CYAN = Color.from_hex_assured("008B8B")
    DARK_GOLDEN_ROD = Color.from_hex_assured("B8860B")
    DARK_GRAY = Color.from_hex_assured("A9A9A9")
    DARK_GREEN = Color.from_hex_assured("006400")
    DARK_KHAKI = Color.from_hex_assured("BDB76B")
    DARK_MAGENTA = Color.from_hex_assured("8B008B")
    DARK_OLIVE_GREEN = Color.from_hex_assured("556B2F")
    DARK_ORANGE = Color.from_hex_assured("FF8C00")
    DARK_ORCHID = Color.from_hex_assured("9932CC")
    DARK_RED = Color.from_hex_assured("8B0000")
    DARK_SALMON = Color.from_hex_assured("E9967A")
    DARK_SEA_GREEN = Color.from_hex_assured("8FBC8F")
    DARK_SLATE_BLUE = Color.from_hex_assured("483D8B")
    DARK_SLATE_GRAY = Color.from_hex_assured("2F4F4F")
    DARK_TURQUOISE = Color.from_hex_assured("00CED1")
    DARK_VIOLET = Color.from_hex_assured("9400D3")
    DEEP_PINK = Color.from_hex_assured("FF1493")
    DEEP_SKY_BLUE = Color.from_hex_assured("00BFFF")
    DIM_GRAY = Color.from_hex_assured("696969")
    DODGER_BLUE = Color.from_hex_assured("1E90FF")
    FIREBRICK = Color.from_hex_assured("B22222")
    FLORAL_WHITE = Color.from_hex_assured("FFFAF0")
    FOREST_GREEN = Color.from_hex_assured("228B22")
    FUCHSIA = Color.from_hex_assured("FF00FF")
    GAINSBORO = Color.from_hex_assured("DCDCDC")
    GHOST_WHITE = Color.from_hex_assured("F8F8FF")
    GOLD = Color.from_hex_assured("FFD700")
    GOLDEN_ROD = Color.from_hex_assured("DAA520")
    GRAY = Color.from_hex_assured("7F7F7F")
    GREEN = Color.from_hex_assured("008000")
    GREEN_YELLOW = Color.from_hex_assured("ADFF2F")
    HONEYDEW = Color.from_hex_assured("F0FFF0")
    HOT_PINK = Color.from_hex_assured("FF69B4")
    INDIAN_RED = Color.from_hex_assured("CD5C5C")
    INDIGO = Color.from_hex_assured("4B0082")
    IVORY = Color.from_hex_assured("FFFFF0")
    KHAKI = Color.from_hex_assured("F0E68C")
    LAVENDER = Color.from_hex_assured("E6E6FA")
    LAVENDER_BLUSH = Color.from_hex_assured("FFF0F5")
    LAWN_GREEN = Color.from_hex_assured("7CFC00")
    LEMON_CHIFFON = Color.from_hex_assured("FFFACD")
    LIGHT_BLUE = Color.from_hex_assured("ADD8E6")
    LIGHT_CORAL = Color.from_hex_assured("F08080")
    LIGHT_CYAN = Color.from_hex_assured("E0FFFF")
    LIGHT_GOLDEN_ROD_YELLOW = Color.from_hex_assured("FAFAD2")
    LIGHT_GREEN = Color.from_hex_assured("90EE90")
    LIGHT_GREY = Color.from_hex_assured("D3D3D3")
    LIGHT_PINK = Color.from_hex_assured("FFB6C1")
    LIGHT_SALMON = Color.from_hex_assured("FFA07A")
    LIGHT_SEA_GREEN = Color.from_hex_assured("20B2AA")
    LIGHT_SKY_BLUE = Color.from_hex_assured("87CEFA")
    LIGHT_SLATE_GRAY = Color.from_hex_assured("778899")
    LIGHT_STEEL_BLUE = Color.from_hex_assured("B0C4DE")
    LIGHT_YELLOW = Color.from_hex_assured("FFFFE0")
    LIME = Color.from_hex_assured("00FF00")
    LIME_GREEN = Color.from_hex_assured("32CD32")
    LINEN = Color.from_hex_assured("FAF0E6")
    MAGENTA = Color.from_hex_assured("FF00FF")
    MAROON = Color.from_hex_assured("800000")
    MEDIUM_AQUAMARINE = Color.from_hex_assured("66CDAA")
    MEDIUM_BLUE = Color.from_hex_assured("0000CD")
    MEDIUM_ORCHID = Color.from_hex_assured("BA55D3")
    MEDIUM_PURPLE = Color.from_hex_assured("9370DB")
    MEDIUM_SEA_GREEN = Color.from_hex_assured("3CB371")
    MEDIUM_SLATE_BLUE = Color.from_hex_assured("7B68EE")
    MEDIUM_SPRING_GREEN = Color.from_hex_assured("00FA9A")
    MEDIUM_TURQUOISE = Color.from_hex_assured("48D1CC")
    MEDIUM_VIOLET_RED = Color.from_hex_assured("C71585")
    MIDNIGHT_BLUE = Color.from_hex_assured("191970")
    MINT_CREAM = Color.from_hex_assured("F5FFFA")
    MISTY_ROSE = Color.from_hex_assured("FFE4E1")
    MOCCASIN = Color.from_hex_assured("FFE4B5")
    NAVAJO_WHITE = Color.from_hex_assured("FFDEAD")
    NAVY = Color.from_hex_assured("000080")
    NAVY_BLUE = Color.from_hex_assured("9FAFDF")
    OLDLACE = Color.from_hex_assured("FDF5E6")
    OLIVE = Color.from_hex_assured("808000")
    OLIVE_DRAB = Color.from_hex_assured("6B8E23")
    ORANGE = Color.from_hex_assured("FFA500")
    ORANGE_RED = Color.from_hex_assured("FF4500")
    ORCHID = Color.from_hex_assured("DA70D6")
    PALE_GOLDEN_ROD = Color.from_hex_assured("EEE8AA")
    PALE_GREEN = Color.from_hex_assured("98FB98")
    PALE_TURQUOISE = Color.from_hex_assured("AFEEEE")
    PALE_VIOLET_RED = Color.from_hex_assured("DB7093")
    PAPAYA_WHIP = Color.from_hex_assured("FFEFD5")
    PEACH_PUFF = Color.from_hex_assured("FFDAB9")
    PERU = Color.from_hex_assured("CD853F")
    PINK = Color.from_hex_assured("FFC0CB")
    PLUM = Color.from_hex_assured("DDA0DD")
    POWDER_BLUE = Color.from_hex_assured("B0E0E6")
    PURPLE = Color.from_hex_assured("800080")
    RED = Color.from_hex_assured("FF0000")
    ROSY_BROWN = Color.from_hex_assured("BC8F8F")
    ROYAL_BLUE = Color.from_hex_assured("4169E1")
    SADDLE_BROWN = Color.from_hex_assured("8B4513")
    SALMON = Color.from_hex_assured("FA8072")
    SANDY_BROWN = Color.from_hex_assured("FA8072")
    SEA_GREEN = Color.from_hex_assured("2E8B57")
    SEASHELL = Color.from_hex_assured("FFF5EE")
    SIENNA = Color.from_hex_assured("A0522D")
    SILVER = Color.from_hex_assured("C0C0C0")
    SKY_BLUE = Color.from_hex_assured("87CEEB")
    SLATE_BLUE = Color.from_hex_assured("6A5ACD")
    SLATE_GRAY = Color.from_hex_assured("708090")
    SNOW = Color.from_hex_assured("FFFAFA")
    SPRING_GREEN = Color.from_hex_assured("00FF7F")
    STEEL_BLUE = Color.from_hex_assured("4682B4")
    TAN = Color.from_hex_assured("D2B48C")
    TEAL = Color.from_hex_assured("008080")
    THISTLE = Color.from_hex_assured("D8BFD8")
    TOMATO = Color.from_hex_assured("FF6347")
    TURQUOISE = Color.from_hex_assured("40E0D0")
    VIOLET = Color.from_hex_assured("EE82EE")
    WHEAT = Color.from_hex_assured("F5DEB3")
    WHITE = Color.from_hex_assured("FFFFFF")
    WHITE_SMOKE = Color.from_hex_assured("F5F5F5")
    YELLOW = Color.from_hex_assured("FFFF00")
    YELLOW_GREEN = Color.from_hex_assured("9ACD32")

    def to_hex(self) -> str:
        if self.value is None:
            raise ValueError("undefined")
        return self.value.to_hex()

    def to_rgb_hex_color(self) -> str:
        return "#" + self.to_hex()


all_color_names = {cv.name.lower().replace("_", ""): cv for cv in ColorValues}
