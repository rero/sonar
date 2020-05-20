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

from flask_security import current_user, url_for_security
from invenio_accounts.testutils import login_user_via_view

from sonar.modules.users.api import UserRecord, UserSearch


def test_get_moderators(app, organisation, roles):
    """Test search for moderators."""
    user = UserRecord.create(
        {
            'full_name': 'John Doe',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR],
            'organisation': {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }
        },
        dbcommit=True)
    user.reindex()

    moderators = UserSearch().get_moderators()
    assert list(moderators)

    moderators = UserSearch().get_moderators('not_existing_organisation')
    assert not list(moderators)


def test_get_user_by_current_user(app, client, user_without_role, user):
    """Test getting a user with email taken from logged user."""
    record = UserRecord.get_user_by_current_user(current_user)
    assert record is None

    login_user_via_view(client,
                        email=user_without_role.email,
                        password='123456')
    record = UserRecord.get_user_by_current_user(current_user)
    assert record is None

    client.get(url_for_security('logout'))

    login_user_via_view(client, email=user['email'], password='123456')
    print(current_user)
    record = UserRecord.get_user_by_current_user(current_user)
    assert 'email' in record
    assert user['email'] == 'org-user@rero.ch'


def test_get_reachable_roles(app):
    """Test get roles covered by the given role."""
    roles = UserRecord.get_reachable_roles(UserRecord.ROLE_MODERATOR)
    assert len(roles) == 3
    assert UserRecord.ROLE_MODERATOR in roles
    assert UserRecord.ROLE_PUBLISHER in roles
    assert UserRecord.ROLE_USER in roles

    roles = UserRecord.get_reachable_roles('unknown_role')
    assert not roles


def test_get_moderators_emails(app, organisation, roles):
    """Test getting list of moderators emails."""
    user = UserRecord.create(
        {
            'full_name': 'John Doe',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR],
            'organisation': {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }
        },
        dbcommit=True)
    user.reindex()

    emails = user.get_moderators_emails()
    assert emails
    assert 'john.doe@rero.ch' in emails

    user['organisation'] = {
        '$ref': 'https://sonar.ch/api/organisations/not-existing'
    }
    emails = user.get_moderators_emails()
    assert not emails


def test_is_granted(app, organisation, roles):
    """Test if user is granted with a role."""
    user = UserRecord.create(
        {
            'full_name': 'John Doe',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR],
            'organisation': {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }
        },
        dbcommit=True)

    assert not user.is_granted(UserRecord.ROLE_ADMIN)
    assert not user.is_granted('fake_role')
    assert user.is_granted(UserRecord.ROLE_MODERATOR)
    assert user.is_granted(UserRecord.ROLE_USER)

    del user['roles']
    assert not user.is_granted(UserRecord.ROLE_MODERATOR)


def test_is_role_property(organisation, roles):
    """Test if user is in a particular role."""
    user = UserRecord.create(
        {
            'full_name': 'John Doe',
            'email': 'john.doe@rero.ch',
            'roles': [UserRecord.ROLE_MODERATOR],
            'organisation': {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }
        },
        dbcommit=True)

    assert user.is_user
    assert user.is_publisher
    assert user.is_moderator
    assert not user.is_admin
    assert not user.is_superuser


def test_delete(app, admin):
    """Test removing record."""
    admin.delete(dbcommit=True, delindex=True)

    deleted = UserRecord.get_record(admin.id,
                                    with_deleted=True)
    assert deleted.id == admin.id

    with app.app_context():
        datastore = app.extensions['security'].datastore
        user = datastore.find_user(email='org-admin@rero.ch')
        assert not user.roles
        assert not user.is_active


def test_update(app, admin, roles):
    """Test updating a record."""
    admin.update({'roles': ['superuser']})
    assert admin['roles'] == ['superuser']

    with app.app_context():
        datastore = app.extensions['security'].datastore
        user = datastore.find_user(email='org-admin@rero.ch')
        assert user.roles[0].name == 'superuser'


def test_reactivate_user(app, admin):
    """Test reactivate user account."""
    with app.app_context():
        datastore = app.extensions['security'].datastore

        user = datastore.find_user(email='org-admin@rero.ch')
        assert user.is_active

        datastore.deactivate_user(user)
        datastore.commit()
        assert not user.is_active

        del admin.__dict__['user']

        admin.update({'roles': ['admin']})
        user = datastore.find_user(email='org-admin@rero.ch')
        assert user.roles[0].name == 'admin'
        assert user.is_active


def test_get_all_reachable_roles(app, db, user):
    """Test getting all reachable roles."""
    user['roles'] = ['user', 'admin']

    roles = user.get_all_reachable_roles()

    assert len(roles) == 4
    assert 'user' in roles
    assert 'moderator' in roles
    assert 'publisher' in roles
    assert 'admin' in roles
