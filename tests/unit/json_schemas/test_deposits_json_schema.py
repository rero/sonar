# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test deposits JSON schema."""

from sonar.jsonschemas.deposits_json_schema import DepositsJSONSchema


class MockUserRecord:
    """Mock user record exposing only what DepositsJSONSchema.process() needs."""

    is_moderator = False

    def __init__(self, organisation):
        """Store the organisation to return."""
        self.organisation = organisation

    def replace_refs(self):
        """Return self, no reference to resolve in this mock."""
        return self

    def get(self, key):
        """Return the mocked organisation."""
        return self.organisation if key == "organisation" else None


def test_process_keeps_new_project_option_by_default(app, monkeypatch):
    """Test the "Add a new project" option is kept when no organisation is restricted."""
    app.config["SONAR_APP_DEPOSITS_DISABLE_NEW_PROJECT_ORGANISATIONS"] = []
    monkeypatch.setattr(
        "sonar.jsonschemas.deposits_json_schema.current_user_record",
        MockUserRecord({"code": "hepvs"}),
    )

    schema = DepositsJSONSchema("deposits").process()

    assert len(schema["properties"]["projects"]["items"]["oneOf"]) == 2


def test_process_removes_new_project_option_for_restricted_organisation(app, monkeypatch):
    """Test the "Add a new project" option is removed for a restricted organisation."""
    app.config["SONAR_APP_DEPOSITS_DISABLE_NEW_PROJECT_ORGANISATIONS"] = ["hepvs"]
    monkeypatch.setattr(
        "sonar.jsonschemas.deposits_json_schema.current_user_record",
        MockUserRecord({"code": "hepvs"}),
    )

    schema = DepositsJSONSchema("deposits").process()

    one_of = schema["properties"]["projects"]["items"]["oneOf"]
    assert len(one_of) == 1
    assert one_of[0]["title"] == "Existing project"


def test_process_keeps_new_project_option_for_other_organisation(app, monkeypatch):
    """Test the "Add a new project" option is kept for a non-restricted organisation."""
    app.config["SONAR_APP_DEPOSITS_DISABLE_NEW_PROJECT_ORGANISATIONS"] = ["hepvs"]
    monkeypatch.setattr(
        "sonar.jsonschemas.deposits_json_schema.current_user_record",
        MockUserRecord({"code": "other"}),
    )

    schema = DepositsJSONSchema("deposits").process()

    assert len(schema["properties"]["projects"]["items"]["oneOf"]) == 2
