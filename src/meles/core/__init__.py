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
from ._color import Color, ColorValues
from ._config import HasConfigItems, config
from ._connect import Request, RequestHandler, Response, Urllib3RequestHandler
from ._context import RequestIDMiddleware
from ._data import BadgeData
from ._error import ProcessingError
from ._falcon import (
    SharedCache,
    SupportsFalconGetRequest,
    SupportsResourceGeneration,
    SupportsResources,
)
from ._generator import Generator
from ._icons import Icon, Icons
from ._log import LOGGER_NAME, LogRecordingMiddleware, get_log_extras, setup_logger
from ._url import TemplateUrlSource, Url, UrlBuilder, UrlSourceBase

__all__ = [
    BadgeData.__name__,
    Generator.__name__,
    ProcessingError.__name__,
    Color.__name__,
    ColorValues.__name__,
    UrlBuilder.__name__,
    UrlSourceBase.__name__,
    Url.__name__,
    TemplateUrlSource.__name__,
    Urllib3RequestHandler.__name__,
    RequestHandler.__name__,
    Request.__name__,
    Response.__name__,
    Icons.__name__,
    Icon.__name__,
    "config",
    setup_logger.__name__,
    get_log_extras.__name__,
    "LOGGER_NAME",
    RequestIDMiddleware.__name__,
    LogRecordingMiddleware.__name__,
    "SharedCache",
    SupportsResources.__name__,
    SupportsResourceGeneration.__name__,
    SupportsFalconGetRequest.__name__,
    HasConfigItems.__name__,
]
