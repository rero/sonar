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

"""Test API for user records."""

from flask_security import current_user
from invenio_accounts.testutils import login_user_via_view
from invenio_search import current_search

from sonar.modules.users.api import UserRecord, UserSearch


def test_get_moderators(app):
    """Test search for moderators."""
    user = UserRecord.create(
        {
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR]
        },
        dbcommit=True)
    user.reindex()

    current_search.flush_and_refresh('users')

    moderators = UserSearch().get_moderators()
    assert list(moderators)

    moderators = UserSearch().get_moderators('not_existing_institution')
    assert not list(moderators)


def test_get_user_by_current_user(app, client, admin_user_fixture):
    """Test getting a user with email taken from logged user."""
    login_user_via_view(client,
                        email=admin_user_fixture.email,
                        password='123456')
    user = UserRecord.get_user_by_current_user(current_user)
    assert user is None

    user = UserRecord.create(
        {
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'admin@test.com',
            'roles': [UserRecord.ROLE_MODERATOR]
        },
        dbcommit=True)
    user.reindex()

    current_search.flush_and_refresh('users')

    user = UserRecord.get_user_by_current_user(current_user)
    assert 'email' in user
    assert user['email'] == 'admin@test.com'


def test_get_reachable_roles(app):
    """Test get roles covered by the given role."""
    roles = UserRecord.get_reachable_roles(UserRecord.ROLE_MODERATOR)
    assert len(roles) == 2
    assert UserRecord.ROLE_MODERATOR in roles
    assert UserRecord.ROLE_USER in roles

    roles = UserRecord.get_reachable_roles('unknown_role')
    assert not roles


def test_get_moderators_emails(app):
    """Test getting list of moderators emails."""
    user = UserRecord.create(
        {
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR]
        },
        dbcommit=True)
    user.reindex()

    current_search.flush_and_refresh('users')

    emails = user.get_moderators_emails()
    assert emails
    assert 'john.doe@rero.ch' in emails

    user['institution'] = {
        '$ref': 'https://sonar.ch/api/institutions/not-existing'
    }
    emails = user.get_moderators_emails()
    assert not emails


def test_is_granted(app):
    """Test if user is granted with a role."""
    user = UserRecord.create(
        {
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR]
        },
        dbcommit=True)

    assert not user.is_granted(UserRecord.ROLE_ADMIN)
    assert not user.is_granted('fake_role')
    assert user.is_granted(UserRecord.ROLE_MODERATOR)
    assert user.is_granted(UserRecord.ROLE_USER)

    del user['roles']
    assert not user.is_granted(UserRecord.ROLE_MODERATOR)


def test_is_role_property():
    """Test if user is in a particular role."""
    user = UserRecord.create(
        {
            'last_name': 'Doe',
            'first_name': 'John',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR]
        },
        dbcommit=True)

    assert user.is_user
    assert user.is_moderator
    assert not user.is_admin
    assert not user.is_super_admin
