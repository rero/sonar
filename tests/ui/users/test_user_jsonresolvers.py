# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test users jsonresolvers."""

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.users.api import UserRecord


def test_user_resolver(app, organisation, roles):
    """Test user resolver."""
    UserRecord.create(
        {
            "pid": "1",
            "first_name": "Jules",
            "last_name": "Brochu",
            "email": "admin@test.com",
            "role": "user",
            "organisation": {"$ref": "https://sonar.ch/api/organisations/org"},
        }
    )

    record = DepositRecord.create(
        {"user": {"$ref": "https://sonar.ch/api/users/1"}, "status": "in_progress"},
        with_bucket=False,
    )

    assert record.replace_refs().get("user")["email"] == "admin@test.com"
