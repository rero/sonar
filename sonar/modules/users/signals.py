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

"""Signals for users."""

from sonar.modules.users.api import UserRecord, datastore


def user_registered_handler(app, user, confirm_token):
    """Called when a new user is registered.

    :param app: App context.
    :param user: User account.
    """
    # Add a default role to user
    role = datastore.find_role(UserRecord.ROLE_USER)
    datastore.add_role_to_user(user, role)
    datastore.commit()


def add_full_name(sender=None, record=None, json=None, index=None, **kwargs):
    """Add full name field in index.

    :param sender: Sender of the signal.
    :param record: Record to index.
    :param json: Indexed data.
    :param index: Index where data is sent.
    """
    # Takes care only about users indexing
    if not index.startswith('users'):
        return

    json['full_name'] = f'{json["first_name"]} {json["last_name"]}'
