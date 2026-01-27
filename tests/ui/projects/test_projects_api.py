# Swiss Open Access Repository
# Copyright (C) 2026 RERO
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
