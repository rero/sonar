# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test dedicated features for HEP-VS."""

from invenio_accounts.testutils import login_user_via_view

from sonar.dedicated.hepvs.projects.schema import RecordSchema
from sonar.proxies import sonar
from sonar.resources.projects.api import Record
from sonar.theme.views import schemas


def test_json_schema(client, make_user):
    """Test JSON schema."""
    user = make_user("admin", "hepvs")

    login_user_via_view(client, email=user["email"], password="123456")

    result = schemas("projects")
    assert result.json["schema"]["properties"]["metadata"]["properties"][
        "projectSponsor"
    ]


def test_service(client, make_user):
    """Test service."""
    user = make_user("admin", "hepvs")

    login_user_via_view(client, email=user["email"], password="123456")

    assert isinstance(sonar.resources["projects"].service.schema.schema(), RecordSchema)


def test_api(client, make_user):
    """Test API."""
    user = make_user("admin", "hepvs")

    login_user_via_view(client, email=user["email"], password="123456")

    assert (
        Record({}).schema.value == "https://sonar.ch/schemas/"
        "hepvs/projects/project-v1.0.0.json"
    )
