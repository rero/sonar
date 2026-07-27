# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test projects API."""

import copy
from unittest import mock

import pytest
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from sonar.modules.validation.api import Action, Status
from sonar.proxies import sonar
from sonar.resources.projects.service import ProjectServiceSchemaWrapper


def test_create_project(admin, organisation, project_json):
    """Test creating a project."""
    # Set the user and organisation in the JSON
    json = copy.deepcopy(project_json)
    json["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{admin['pid']}"}
    json["metadata"]["organisation"] = {"$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"}

    service = sonar.service("projects")
    with (
        mock.patch("invenio_records_resources.services.base.service.Service.require_permission"),
    ):
        project = service.create(None, json)
        assert project

        del json["metadata"]["name"]
        with pytest.raises(MarshmallowValidationError):
            # Marshmallow validation should fail
            service.create(None, json)
        with (
            # disable the marshmallow validation
            mock.patch.object(
                ProjectServiceSchemaWrapper,
                "load",
                side_effect=lambda data, *a, **kw: (data, {}),
            ),
            pytest.raises(JsonSchemaValidationError),
        ):
            # JSON Schema validation should fail
            service.create(None, json)


def test_create_project_hepvs(app, admin, make_organisation, project_hepvs_json):
    """Test creating a HEPVS project."""
    # Set the user and organisation in the JSON
    organisation = make_organisation(code="hepvs")
    json = copy.deepcopy(project_hepvs_json)
    json["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{admin['pid']}"}
    json["metadata"]["organisation"] = {"$ref": f"https://sonar.ch/api/organisations/{organisation['pid']}"}
    json["metadata"]["validation"] = {
        "status": Status.IN_PROGRESS,
        "action": Action.SAVE,
        "user": {"$ref": f"https://sonar.ch/api/users/{admin['pid']}"},
    }

    service = sonar.service("projects")
    with (
        mock.patch("invenio_records_resources.services.base.service.Service.require_permission"),
    ):
        project = service.create(None, json)
        assert project

        del json["metadata"]["name"]
        with pytest.raises(MarshmallowValidationError):
            # Marshmallow validation should fail
            service.create(None, json)
        with (
            # disable the marshmallow validation
            mock.patch.object(
                ProjectServiceSchemaWrapper,
                "load",
                side_effect=lambda data, *a, **kw: (data, {}),
            ),
            pytest.raises(JsonSchemaValidationError),
        ):
            # JSON Schema validation should fail
            service.create(None, json)
