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
import pytest


@pytest.fixture
def use_prometheus():
    return True


def test_metrics_ok(client):
    response = client.get("/metrics")
    assert response.status == falcon.HTTP_200
    assert len(response.body) > 0


def test_metrics_content(client):
    response = client.get("/metrics")
    lines = response.body.splitlines()
    assert len(lines) > 0
    assert len([ln for ln in lines if not ln.startswith('#')]) == 0
