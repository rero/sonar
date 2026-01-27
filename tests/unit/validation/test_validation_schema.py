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

"""Test validation schema."""

from invenio_accounts.testutils import login_user_via_view

from sonar.dedicated.hepvs.projects.schema import MetadataSchema as HepvsMetadataSchema
from sonar.resources.projects.schema import MetadataSchema as StandardMetadataSchema


def test_add_validation_data_with_hepvs(app, client, make_organisation, make_user, roles):
    """Test validation data is added for HEPVS organisation."""
    make_organisation(code="hepvs", is_shared=False)
    user = make_user(role_name="submitter", organisation="hepvs", access="admin-access")
    login_user_via_view(client, email=user["email"], password="123456")

    schema = HepvsMetadataSchema()
    result = schema.load({"name": "Test project"})

    assert "validation" in result
    assert result["validation"]["status"] == "in_progress"
    assert result["validation"]["action"] == "save"
    assert "user" in result["validation"]


def test_add_validation_data_with_standard_org(app, client, organisation, submitter):
    """Test validation data is NOT added for standard organisation."""
    login_user_via_view(client, email=submitter["email"], password="123456")

    schema = StandardMetadataSchema()
    result = schema.load({"name": "Test project"})

    assert "validation" not in result


def test_standard_schema_does_not_accept_validation_field(app, client, organisation, submitter):
    """Test standard schema does not have validation field."""
    login_user_via_view(client, email=submitter["email"], password="123456")

    schema = StandardMetadataSchema()
    # Standard schema doesn't have validation field, so it's not in the declared fields
    assert "validation" not in schema.declared_fields
