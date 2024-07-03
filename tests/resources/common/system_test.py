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
from packaging.version import Version


def test_system_ok(client):
    response = client.get("/system")
    assert response.status == falcon.HTTP_200


def test_system_name(client):
    response = client.get("/system")
    assert response.json["name"] == "meles"


def test_system_version(client):
    response = client.get("/system")
    version = response.json["version"]
    version_object = Version(version)
    assert version_object > Version("0.0.0")


def test_system_license(client):
    response = client.get("/system")
    assert response.json["license"] == "AGPL-3.0"


def test_system_dependencies(client):
    response = client.get("/system")
    assert len(response.json["dependencies"]) > 0


def test_system_routes(client):
    response = client.get("/system")
    assert len(response.json["routes"]) > 0


def test_system_routes_system(client):
    response = client.get("/system")
    assert "/system" in response.json["routes"]


def test_system_routes_health(client):
    response = client.get("/system")
    assert "/health" in response.json["routes"]


def test_system_routes_metrics(client):
    response = client.get("/system")
    assert "/metrics" in response.json["routes"]


def test_system_urls(client):
    response = client.get("/system")
    assert len(response.json["urls"]) > 0


def test_system_urls_homepage(client):
    response = client.get("/system")
    assert "Homepage" in response.json["urls"] and len(response.json["urls"]["Homepage"]) > 0


def test_system_urls_repository(client):
    response = client.get("/system")
    assert "Repository" in response.json["urls"] and len(response.json["urls"]["Repository"]) > 0


def test_system_urls_documentation(client):
    response = client.get("/system")
    assert "Documentation" in response.json["urls"] and len(response.json["urls"]["Documentation"]) > 0
