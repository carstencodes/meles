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

from .core._url import Url
from .family.custom import CustomFamily
from .family.nuget import NugetFamily
from .family.shield import ShieldFamily

from .sources import custom as _custom_sources
from .sources.custom.base import CustomBackendSource as _CustomBackendSource
from .sources.base import SourcesCollection as _SourcesCollection

if TYPE_CHECKING:  # pragma: no cover
    from .core import SupportsResources


_all_sources: "_SourcesCollection" = _SourcesCollection(_custom_sources)


_DEFAULT_NUGET_FEED_V3_URL = "https://api.nuget.org/v3/index.json"


def configure(app: "SupportsResources") -> None:
    app.add_family(
        NugetFamily(Url.static(_DEFAULT_NUGET_FEED_V3_URL).source),
    )
    app.add_family(ShieldFamily())
    app.add_family(CustomFamily(_all_sources.get_sources(type_to_bind=_CustomBackendSource)))
