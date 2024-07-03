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
from typing import TYPE_CHECKING

from pybadges import badge

from ._color import ColorValues

if TYPE_CHECKING:  # pragma: no cover
    from ._data import BadgeData


class Generator:
    def transform(self, badge_data: "BadgeData") -> str:
        return badge(
            left_text=badge_data.label,
            right_text=badge_data.text,
            left_color=f"#{ColorValues.BLACK.to_hex()}",
            right_color=f"#{badge_data.color.to_hex()}",
            logo=badge_data.icon.encode_as_data_url()
            if badge_data.icon is not None
            else None,
        )
