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

"""Test validation API."""

import pytest
from flask_security import url_for_security
from invenio_accounts.testutils import login_user_via_view

from sonar.modules.users.exceptions import (
    UserIsNotOwnerOfRecordError,
    UserNotLoggedError,
    UserRecordNotFoundError,
)
from sonar.modules.validation.api import Validation


def test_load_user(client, submitter, moderator):
    """Test load user."""
    validation = Validation()

    # User not logged
    with pytest.raises(Exception) as exception:
        validation._load_user({"metadata": {"validation": {}}})
        assert isinstance(exception.value, UserNotLoggedError)

    login_user_via_view(client, email=submitter["email"], password="123456")

    # No user in record
    with pytest.raises(Exception) as exception:
        validation._load_user({"metadata": {"validation": {}}})
        assert str(exception.value) == "No user stored in record"

    # No user in record
    with pytest.raises(Exception) as exception:
        validation._load_user(
            {
                "metadata": {
                    "validation": {
                        "user": {"$ref": "https://sonar.ch/api/users/not-existing"}
                    }
                }
            }
        )
        assert isinstance(exception.value, UserRecordNotFoundError)

    # Logged user is not owner of the record
    with pytest.raises(Exception) as exception:
        validation._load_user(
            {
                "metadata": {
                    "validation": {
                        "user": {
                            "$ref": f'https://sonar.ch/api/users/{moderator["pid"]}'
                        }
                    }
                }
            }
        )
        assert isinstance(exception.value, UserIsNotOwnerOfRecordError)


def test_submitter_process(client, submitter, project):
    """Test validation process."""
    validation = Validation()

    # No validation metadata
    record = {}
    validation.process(record)
    assert record == {}

    # User is not logged
    record = {"metadata": {"validation": {"status": "in_progress"}}}
    validation.process(record)
    assert record == {"metadata": {"validation": {"status": "in_progress"}}}

    login_user_via_view(client, email=submitter["email"], password="123456")

    # Save the record, the status is back in progress
    for status in ["to_validate", "validated"]:
        project._record["metadata"]["validation"]["status"] = status
        validation.process(project._record)
        assert project._record["metadata"]["validation"]["status"] == "in_progress"

    project._record["metadata"]["validation"]["action"] = "publish"

    # Publish the record
    for status in ["in_progress", "ask_for_changes"]:
        project._record["metadata"]["validation"]["status"] = status
        validation.process(project._record)
        assert project._record["metadata"]["validation"]["status"] == "to_validate"


def test_moderator_process(client, moderator, project):
    """Test moderator validation process."""
    login_user_via_view(client, email=moderator["email"], password="123456")

    validation = Validation()

    # Save a record and the moderator is the owner
    project._record["metadata"]["validation"]["user"][
        "$ref"
    ] = f'https://sonar.ch/api/users/{moderator["pid"]}'
    for status in ["in_progress", "to_validate", "ask_for_changes", "rejected"]:
        project._record["metadata"]["validation"]["status"] = status
        validation.process(project._record)
        assert project._record["metadata"]["validation"]["status"] == "validated"

    # Ask for changes
    project._record["metadata"]["validation"]["action"] = "ask_for_changes"
    project._record["metadata"]["validation"]["status"] = "to_validate"
    validation.process(project._record)
    assert project._record["metadata"]["validation"]["status"] == "ask_for_changes"

    # Rejected
    project._record["metadata"]["validation"]["action"] = "reject"
    project._record["metadata"]["validation"]["status"] = "to_validate"
    validation.process(project._record)
    assert project._record["metadata"]["validation"]["status"] == "rejected"

    # Approved
    project._record["metadata"]["validation"]["action"] = "approve"
    project._record["metadata"]["validation"]["status"] = "to_validate"
    validation.process(project._record)
    assert project._record["metadata"]["validation"]["status"] == "validated"


def test_user_is_owner_of_record(client, submitter, moderator):
    """Test if user is owner of the record."""
    validation = Validation()

    # Is owner
    login_user_via_view(client, email=submitter["email"], password="123456")
    assert validation._user_is_owner_of_record({"pid": submitter["pid"]})

    # Is not owner
    login_user_via_view(client, email=moderator["email"], password="123456")
    assert validation._user_is_owner_of_record({"pid": submitter["pid"]})


def test_user_can_moderate(client, submitter, moderator):
    """Test if user can moderate the record."""
    validation = Validation()

    # No logged user
    assert not validation._user_can_moderate()

    # Not moderator
    login_user_via_view(client, email=submitter["email"], password="123456")
    assert not validation._user_can_moderate()

    client.get(url_for_security("logout"))

    # Moderator
    login_user_via_view(client, email=moderator["email"], password="123456")
    assert validation._user_can_moderate()


def test_update_status(client, submitter):
    """Test validation status update."""
    login_user_via_view(client, email=submitter["email"], password="123456")

    validation = Validation()
    validation_data = {
        "status": "to_validate",
        "action": "approve",
        "comment": "My comment",
    }
    validation._update_status(validation_data, "validated")
    assert not validation_data.get("comment")
    assert validation_data["logs"][0]["status"] == "validated"


def test_send_email(app, submitter, moderator):
    """Test send_email."""
    validation = Validation()
    # Without recipients
    with pytest.raises(Exception) as exception:
        validation._send_email([], "validated")
    assert str(exception.value) == "No recipients found in list"

    # Recipients is not a list
    with pytest.raises(Exception) as exception:
        validation._send_email("test", "validated")
    assert str(exception.value) == "No recipients found in list"

    # Send OK
    record = {"pid": {"pid_value": "100"}, "index_name": "projects"}
    validation._send_email(
        [submitter["email"]],
        "validated",
        user=submitter,
        moderator=moderator,
        record=record,
        app=app,
    )
