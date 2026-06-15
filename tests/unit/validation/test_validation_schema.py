# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
