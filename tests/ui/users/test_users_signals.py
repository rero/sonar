# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test signals for users."""

from sonar.modules.users.api import UserRecord
from sonar.modules.users.signals import user_registered_handler


def test_user_registered_handler(app, roles, user_without_role):
    """Test user confirmed signal."""
    assert not user_without_role.roles
    user_registered_handler(app, user_without_role, None)
    assert user_without_role.roles[0].name == "user"

    user = UserRecord.get_user_by_email(user_without_role.email)
    assert not user
