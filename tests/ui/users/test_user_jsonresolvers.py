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

"""Test users jsonresolvers."""

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.users.api import UserRecord


def test_user_resolver(app, organisation, roles):
    """Test user resolver."""
    UserRecord.create({
        'pid': '1',
        'first_name': 'Jules',
        'last_name': 'Brochu',
        'email': 'admin@test.com',
        'role': 'user',
        'organisation': {
            '$ref': 'https://sonar.ch/api/organisations/org'
        }
    })

    record = DepositRecord.create(
        {'user': {
            '$ref': 'https://sonar.ch/api/users/1'
        },
        'status': 'in_progress'}, with_bucket=False)

    assert record.replace_refs().get('user')['email'] == 'admin@test.com'
