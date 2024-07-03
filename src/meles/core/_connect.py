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
import http
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Mapping, cast, get_args
from urllib.parse import urlparse

from certifi import where as locate_certificates
from urllib3 import HTTPSConnectionPool
from urllib3.exceptions import HTTPError

from ._error import ProcessingError
from ._log import LOGGER_NAME
from ._url import Url

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Callable


class RequestHandler(ABC):
    @abstractmethod
    def handle_request(self, request: "Request") -> "Response":
        ...


class Urllib3RequestHandler(RequestHandler):
    def __init__(
        self, request_certs: "Callable[[], str]" = locate_certificates
    ) -> None:
        self.__locations_of_certs = request_certs()
        self.__logger = logging.getLogger(LOGGER_NAME)

    def handle_request(self, request: "Request") -> "Response":
        request_args: "dict[str, Any]" = asdict(request)
        del request_args["url"]

        url = urlparse(str(request.url))

        self.__logger.debug("Performing request to %s", request.url)
        try:
            pool = HTTPSConnectionPool(
                url.netloc,
                url.port or 443,
                cert_reqs="CERT_REQUIRED",
                ca_certs=self.__locations_of_certs,
            )
            response_data = pool.request("GET", str(request.url), **request_args)
            content = response_data.data
            self.__logger.debug(
                "Request to %s returned: %s; status: %s",
                request.url,
                content,
                response_data.status,
            )
            return Response(
                str(request.url),
                response_data.headers,
                response_data.status,
                content,
            )
        except HTTPError as hexc:
            raise ProcessingError(
                http.HTTPStatus.BAD_GATEWAY,
                f"Failed to send request to {request.url}",
            ) from hexc


@dataclass
class Request:  # pylint: disable=R0902
    url: Url = field()
    body: "bytes | None" = field(default=None)
    fields: "Mapping[str, Any] | None" = field(default=None)
    headers: "Mapping[str, str] | None" = field(default=None)
    preload_content: "bool | None" = field(default=True)
    decode_content: "bool | None" = field(default=True)
    redirect: "bool | None" = field(default=True)
    retries: "bool | int | None" = field(default=None)
    timeout: "float | int | None" = field(default=3, metadata={"unit": "seconds"})
    json: "Any | None" = field(default=None)


@dataclass
class Response:
    url: str = field()
    headers: "Mapping[str, str] | Mapping[bytes, bytes] | None" = field(default=None)
    status: "int" = field(default=http.HTTPStatus.NO_CONTENT.value)
    data: "bytes | None" = field(default=None)

    def has_header(self, header_key: str) -> bool:
        return self._get_raw_header(header_key) is not None

    def get_header(self, header_key: str) -> str:
        value = self._get_raw_header(header_key)
        if value is None:
            return ""

        if isinstance(value, bytes):
            return value.decode("utf-8")
        elif isinstance(value, str):
            return value

        return ""

    def _get_raw_header(self, header_key: str) -> "str | bytes | None":
        if self.headers is not None:
            return None

        args = get_args(self.headers)
        if args[0] == str:
            return cast(Mapping[str, str], self.headers).get(header_key)

        elif args[0] == bytes:
            return cast(Mapping[bytes, bytes], self.headers).get(
                header_key.encode("utf-8")
            )

        return None
