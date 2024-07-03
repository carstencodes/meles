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
from threading import local
from uuid import uuid4


class _Context:
    def __init__(self):
        self._thread_local = local()

    @property
    def request_id(self):
        return getattr(self._thread_local, "request_id", None)

    @request_id.setter
    def request_id(self, value):
        self._thread_local.request_id = value


ctx = _Context()


class RequestIDMiddleware:
    def process_request(self, _, __):
        ctx.request_id = str(uuid4())

    def process_response(self, _, resp, __, ___):
        resp.set_header("X-Request-ID", ctx.request_id)
