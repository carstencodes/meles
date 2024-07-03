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
from datetime import datetime
from json import dumps as to_json
from logging import (
    DEBUG,
    INFO,
    Formatter,
    Logger,
    LogRecord,
    StreamHandler,
    getLogger,
    getLoggerClass,
    setLoggerClass,
)
from sys import stderr
from traceback import format_exception
from typing import TYPE_CHECKING

from ._context import ctx

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType
    from typing import Final, Mapping

    from falcon import Request, Response  # type: ignore


LOGGER_NAME: "Final[str]" = "meles"
EMPTY_RECORD: "Final[LogRecord]" = LogRecord(
    LOGGER_NAME, DEBUG, __file__, -1, "EMPTY", None, None
)
EMPTY_RECORD_DATA: "Final[list[str]]" = dir(EMPTY_RECORD)


_logger_initialized: bool = False


class _JsonFormatter(Formatter):
    def formatTime(self, record: "LogRecord", datefmt=None) -> str:
        timestamp: datetime = datetime.fromtimestamp(record.created)
        if datefmt is not None:
            return timestamp.strftime(datefmt)
        return timestamp.isoformat()

    def formatException(
        self,
        ei: "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None]",
    ) -> str:
        instance: dict = {}
        type_info, exception, _ = ei
        if type_info is not None:
            instance["type"] = type_info.__name__
        else:
            instance["type"] = "<unknown>"
        if exception is not None:
            instance["exception"] = exception.args
        else:
            instance["exception"] = tuple()
        instance["traceback"] = format_exception(exception)

        return to_json(instance)

    def formatStack(self, stack_info) -> str:
        return stack_info

    def format(self, record: "LogRecord") -> str:
        instance: dict = {
            "created": self.formatTime(record),
            "levelName": record.levelname or "",
            "fileName": record.filename or "",
            "lineno": record.lineno or "",
            "funcName": record.funcName or "",
            "module": record.module or "",
            "msg": record.msg or "",
            "exc_info": ""
            if record.exc_info is None
            else self.formatException(record.exc_info),
            "stack_info": record.stack_info or "",
            "threadName": record.threadName or "",
            "thread": record.thread or "",
            "process": record.process or "",
            "processName": record.processName or "",
        }

        if isinstance(record.args, (tuple, list)):
            instance["args"] = record.args
        elif isinstance(record.args, dict):
            for key, value in record.args.items():
                if key not in instance:
                    instance[f"{key}"] = value
                else:
                    instance[f"args_{key}"] = value
        instance["message"] = record.getMessage() or ""
        extras: list = [a for a in dir(record) if a not in EMPTY_RECORD_DATA]
        extra_data: dict = {e: getattr(record, e) for e in extras}
        if len(extra_data) > 0:
            instance["extras"] = extra_data
        for key, value in extra_data.items():
            if key.startswith("meles."):
                key = key[len("meles.") :]
                if key not in instance:
                    instance[key] = value

        return to_json(instance)


class _RequestEnrichingLogger(Logger):
    def makeRecord(  # pylint: disable=R0913
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args: "tuple[object, ...] | Mapping[str, object]",
        exc_info: "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None",
        func: "str | None" = None,
        extra: "Mapping[str, object] | None" = None,
        sinfo: "str | None" = None,
    ) -> "LogRecord":
        result_value: "LogRecord" = super().makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )
        rid = ctx.request_id
        if rid is not None:
            result_value.__dict__["meles.request_id"] = rid
        else:
            result_value.__dict__["meles.request_id"] = "__main__"

        return result_value


def setup_logger(enable_debug: bool = False):
    global _logger_initialized  #
    if _logger_initialized:
        return

    old_cls = getLoggerClass()
    setLoggerClass(_RequestEnrichingLogger)
    logger: "Logger" = getLogger(LOGGER_NAME)
    setLoggerClass(old_cls)
    logger.setLevel(DEBUG if enable_debug else INFO)
    stderr_handler = StreamHandler(stderr)
    stderr_handler.setFormatter(_JsonFormatter())
    logger.addHandler(stderr_handler)
    _logger_initialized = True


def get_log_extras(**kwargs) -> dict:
    return kwargs


class LogRecordingMiddleware:
    def __init__(self) -> None:
        self.__log = getLogger(LOGGER_NAME)

    def process_request(self, req: "Request", _):
        self.__log.debug("Processing request '%s'", req.url)

    def process_response(
        self, req: "Request", resp: "Response", _, req_succeeded: bool
    ):
        self.__log.debug(
            "Processing %s response for request with url '%s'. Result: %s.",
            "successful" if req_succeeded else "failed",
            req.url,
            resp.status,
        )
