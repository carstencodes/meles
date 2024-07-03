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

import falcon
import json


def test_routes_ok(client):
    response = client.get("/_all_routes")
    assert response.status == falcon.HTTP_200


def test_routes_count(client):
    response = client.get("/_all_routes")
    routes = json.loads(response.body)
    assert len(routes) == 0


def test_routes_system(client):
    response = client.get("/_all_routes")
    routes = json.loads(response.body)
    assert "/system" not in routes


def test_routes_metrics(client):
    response = client.get("/_all_routes")
    routes = json.loads(response.body)
    assert "/metrics" not in routes


def test_routes_health(client):
    response = client.get("/_all_routes")
    routes = json.loads(response.body)
    assert "/health" not in routes
