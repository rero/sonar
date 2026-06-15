# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
    assert result.json["schema"]["properties"]["metadata"]["properties"]["projectSponsor"]


def test_service(client, make_user):
    """Test service wrapper selects HEPVS schema for HEPVS org data."""
    make_user("admin", "hepvs")

    # The schema wrapper dynamically selects schema based on organisation
    service_schema = sonar.resources["projects"].service.schema
    data = {"metadata": {"name": "Test", "organisation": {"$ref": "https://sonar.ch/api/organisations/hepvs"}}}

    # Trigger schema selection
    service_schema._set_schema(data)

    # After setting schema for HEPVS data, the schema should be HEPVS RecordSchema
    assert service_schema.schema == RecordSchema


def test_api(client, make_user):
    """Test API that HEPVS JSON schema is used for HEPVS organisation records."""
    make_user("admin", "hepvs")

    # JSON schema is based on the record's organisation, not current user
    record_data = {"metadata": {"organisation": {"$ref": "https://sonar.ch/api/organisations/hepvs"}}}

    # Access the field class directly from Record class to test _get_schema
    schema_field = Record.schema
    assert schema_field._get_schema(record_data) == "https://sonar.ch/schemas/hepvs/projects/project-v1.0.0.json"
