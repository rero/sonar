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

"""Test API for user records."""

from sonar.modules.users.api import UserRecord, UserSearch


def test_get_moderators(app, db, organisation, subdivision, roles, search_clear):
    """Test search for moderators."""
    for item in [
        {
            "email": "moderator@gmail.com",
            "role": UserRecord.ROLE_MODERATOR,
            "subdivision": False,
        },
        {
            "email": "moderator+subdivision@gmail.com",
            "role": UserRecord.ROLE_MODERATOR,
            "subdivision": True,
        },
        {
            "email": "admin@gmail.com",
            "role": UserRecord.ROLE_ADMIN,
            "subdivision": False,
        },
        {
            "email": "admin+subdivision@gmail.com",
            "role": UserRecord.ROLE_ADMIN,
            "subdivision": True,
        },
    ]:
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": item["email"],
            "role": item["role"],
            "organisation": {"$ref": "https://sonar.ch/api/organisations/org"},
        }

        if item["subdivision"]:
            data["subdivision"] = {
                "$ref": f'https://sonar.ch/api/subdivisions/{subdivision["pid"]}'
            }
        user = UserRecord.create(data, dbcommit=True)
        user.reindex()

    moderators = [result["email"] for result in UserSearch().get_moderators()]
    assert "moderator@gmail.com" in moderators
    assert "admin@gmail.com" in moderators
    assert "admin+subdivision@gmail.com" in moderators

    moderators = [
        result["email"]
        for result in UserSearch().get_moderators("not_existing_organisation")
    ]
    assert not moderators

    moderators = [result["email"] for result in UserSearch().get_moderators("org")]
    assert "moderator@gmail.com" in moderators
    assert "admin@gmail.com" in moderators
    assert "admin+subdivision@gmail.com" in moderators

    # Get moderators from the same subdivision
    moderators = [
        result["email"]
        for result in UserSearch().get_moderators("org", subdivision["pid"])
    ]
    assert "moderator+subdivision@gmail.com" in moderators
    assert "admin@gmail.com" in moderators
    assert "admin+subdivision@gmail.com" in moderators


def test_get_reachable_roles(app):
    """Test get roles covered by the given role."""
    roles = UserRecord.get_reachable_roles(UserRecord.ROLE_MODERATOR)
    assert len(roles) == 3
    assert UserRecord.ROLE_MODERATOR in roles
    assert UserRecord.ROLE_SUBMITTER in roles
    assert UserRecord.ROLE_USER in roles

    roles = UserRecord.get_reachable_roles("unknown_role")
    assert not roles


def test_get_moderators_emails(app, organisation, roles):
    """Test getting list of moderators emails."""
    user = UserRecord.create(
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@rero.ch",
            "role": UserRecord.ROLE_MODERATOR,
            "organisation": {"$ref": "https://sonar.ch/api/organisations/org"},
        },
        dbcommit=True,
    )
    user.reindex()

    emails = user.get_moderators_emails()
    assert emails
    assert "john.doe@rero.ch" in emails

    user["organisation"] = {"$ref": "https://sonar.ch/api/organisations/not-existing"}
    emails = user.get_moderators_emails()
    assert not emails


def test_is_granted(app, organisation, roles):
    """Test if user is granted with a role."""
    user = UserRecord.create(
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@rero.ch",
            "role": UserRecord.ROLE_MODERATOR,
            "organisation": {"$ref": "https://sonar.ch/api/organisations/org"},
        },
        dbcommit=True,
    )

    assert not user.is_granted(UserRecord.ROLE_ADMIN)
    assert not user.is_granted("fake_role")
    assert user.is_granted(UserRecord.ROLE_MODERATOR)
    assert user.is_granted(UserRecord.ROLE_USER)

    del user["role"]
    assert not user.is_granted(UserRecord.ROLE_MODERATOR)


def test_is_role_property(organisation, roles):
    """Test if user is in a particular role."""
    user = UserRecord.create(
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@rero.ch",
            "role": UserRecord.ROLE_MODERATOR,
            "organisation": {"$ref": "https://sonar.ch/api/organisations/org"},
        },
        dbcommit=True,
    )

    assert user.is_user
    assert user.is_submitter
    assert user.is_moderator
    assert not user.is_admin
    assert not user.is_superuser


def test_delete(app, admin):
    """Test removing record."""
    admin.delete(dbcommit=True, delindex=True)

    deleted = UserRecord.get_record(admin.id, with_deleted=True)
    assert deleted.id == admin.id

    # the user still exist and should have only the user role
    with app.app_context():
        datastore = app.extensions["security"].datastore
        user = datastore.find_user(email="orgadmin@rero.ch")
        assert user.roles == [datastore.find_role("user")]


def test_update(app, admin, roles):
    """Test updating a record."""
    admin.update({"role": "superuser"})
    assert admin["role"] == "superuser"

    with app.app_context():
        datastore = app.extensions["security"].datastore
        user = datastore.find_user(email="orgadmin@rero.ch")
        assert user.roles[0].name == "superuser"


def test_reactivate_user(app, admin):
    """Test reactivate user account."""
    with app.app_context():
        datastore = app.extensions["security"].datastore

        user = datastore.find_user(email="orgadmin@rero.ch")
        assert user.is_active

        datastore.deactivate_user(user)
        datastore.commit()
        assert not user.is_active

        del admin.__dict__["user"]

        admin.update({"role": "admin"})
        user = datastore.find_user(email="orgadmin@rero.ch")
        assert user.roles[0].name == "admin"
        assert user.is_active


def test_get_all_reachable_roles(app, db, user):
    """Test getting all reachable roles."""
    user["role"] = "admin"

    roles = user.get_all_reachable_roles()

    assert len(roles) == 4
    assert "user" in roles
    assert "moderator" in roles
    assert "submitter" in roles
    assert "admin" in roles
