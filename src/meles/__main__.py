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
import logging
from typing import TYPE_CHECKING
from wsgiref.simple_server import WSGIRequestHandler, make_server

from .app import get_app
from .core import LOGGER_NAME, config, setup_logger

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class _StructuredLoggingWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, fmt: str, *args: "Any"):  # pylint: disable=W0221
        message = fmt % args
        logging.getLogger(LOGGER_NAME).debug(
            "%s - - [%s] %s\n",
            self.address_string(),
            self.log_date_time_string(),
            message,
        )


if __name__ == "__main__":
    setup_logger(config.env.is_development)
    logger = logging.getLogger(LOGGER_NAME)
    if config.env.is_development:
        with make_server(
            config.host or "127.0.0.1",
            config.port or 8080,
            get_app(),
            handler_class=_StructuredLoggingWSGIRequestHandler,
        ) as httpd:
            logger.info("Serving on http://%s:%i", config.host, config.port)
            # Origin: https://stackoverflow.com/a/35576127
            # Copyright 2016, Vianney Bajart
            # Licensed under CC-BY-SA
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("Received shutdown request")
            finally:
                httpd.server_close()
                logger.info("Server shut-down")
    else:
        logger.warning("Not running on development mode")
