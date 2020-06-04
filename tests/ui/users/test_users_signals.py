# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Test signals for users."""

from sonar.modules.users.api import UserRecord
from sonar.modules.users.signals import user_registered_handler


def test_user_registered_handler(app, roles, user_without_role):
    """Test user confirmed signal."""
    assert not user_without_role.roles
    user_registered_handler(app, user_without_role, None)
    assert user_without_role.roles[0].name == 'user'

    user = UserRecord.get_user_by_email(user_without_role.email)
    assert user
    assert user['roles'] == ['user']
