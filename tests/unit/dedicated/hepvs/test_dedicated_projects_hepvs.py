# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test dedicated features for HEP-VS."""

from invenio_accounts.testutils import login_user_via_view

from sonar.dedicated.hepvs.projects.serializers.csv import CSVSerializer
from sonar.proxies import sonar
from sonar.resources.projects.api import Record
from sonar.theme.views import schemas


def test_json_schema(client, make_user):
    """Test JSON schema."""
    user = make_user("admin", "hepvs")

    login_user_via_view(client, email=user["email"], password="123456")

    result = schemas("projects")
    assert result.json["schema"]["properties"]["metadata"]["properties"]["projectSponsor"]


def test_service(app):
    """Test service wrapper uses the HEPVS schema for HEPVS org data only."""
    service_schema = sonar.resources["projects"].service.schema
    default_schema = service_schema.schema
    hepvs_metadata = {
        "name": "Test",
        "projectSponsor": "Sponsor",
        "organisation": {"$ref": "https://sonar.ch/api/organisations/hepvs"},
        "validation": {"status": "in_progress", "action": "save", "user": {"$ref": "https://sonar.ch/api/users/1"}},
    }

    data, errors = service_schema.load({"metadata": hepvs_metadata})
    assert data["metadata"]["projectSponsor"] == "Sponsor"
    assert not errors

    # The HEPVS schema does not stick to the wrapper.
    assert service_schema.schema is default_schema
    _, errors = service_schema.load({"metadata": {"name": "Test", "projectSponsor": "Sponsor"}}, raise_errors=False)
    assert errors


def test_api(client, make_user):
    """Test API that HEPVS JSON schema is used for HEPVS organisation records."""
    make_user("admin", "hepvs")

    # JSON schema is based on the record's organisation, not current user
    record_data = {"metadata": {"organisation": {"$ref": "https://sonar.ch/api/organisations/hepvs"}}}

    # Access the field class directly from Record class to test _get_schema
    schema_field = Record.schema
    assert schema_field._get_schema(record_data) == "https://sonar.ch/schemas/hepvs/projects/project-v1.0.0.json"


def test_csv_format_row_without_conditional_fields():
    """Test CSV row formatting when conditional sub-fields are not stored."""
    data = {
        "externalPartners": {"choice": True},
        "educationalDocument": {"choice": True},
        "promoteInnovation": {"choice": True},
        "actorsInvolved": [{"choice": "Other", "count": 2}],
    }

    CSVSerializer().format_row(data)

    assert data == {
        "externalPartners": "",
        "educationalDocument": "",
        "promoteInnovation": "",
        "actorsInvolved": "Other (2)",
    }
