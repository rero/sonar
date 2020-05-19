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

"""User Api."""

from functools import partial

from elasticsearch_dsl.query import Q
from flask import current_app
from flask_security.confirmable import confirm_user
from flask_security.recoverable import send_reset_password_instructions
from invenio_accounts.ext import hash_password
from werkzeug.local import LocalProxy
from werkzeug.utils import cached_property

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
UserProvider = type('UserProvider', (Provider, ), dict(pid_type='user'))
# minter
user_pid_minter = partial(id_minter, provider=UserProvider)
# fetcher
user_pid_fetcher = partial(id_fetcher, provider=UserProvider)

datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


class UserSearch(SonarSearch):
    """Search users."""

    class Meta:
        """Search only on item index."""

        index = 'users'
        doc_types = []

    def get_moderators(self, organisation_pid=None):
        """Get moderators corresponding to organisation.

        If no organisation provided, return moderators not associated with
        organisations.
        """
        filter_roles = []
        roles = UserRecord.get_all_roles_for_role(UserRecord.ROLE_MODERATOR)
        for role in roles:
            filter_roles.append(Q('term', roles=role))

        query = self.query(
            'bool',
            filter=[Q('bool', should=filter_roles, minimum_should_match=1)])

        if organisation_pid:
            query = query.filter('term', organisation__pid=organisation_pid)

        return query.source(includes=['pid', 'email']).scan()


class UserRecord(SonarRecord):
    """User record class."""

    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLE_SUPERADMIN = 'superadmin'

    ROLES_HIERARCHY = {
        ROLE_USER: [],
        ROLE_MODERATOR: [ROLE_USER],
        ROLE_ADMIN: [ROLE_MODERATOR, ROLE_USER],
        ROLE_SUPERADMIN: [ROLE_ADMIN, ROLE_MODERATOR, ROLE_USER],
    }

    minter = user_pid_minter
    fetcher = user_pid_fetcher
    provider = UserProvider
    schema = 'users/user-v1.0.0.json'
    available_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_MODERATOR, ROLE_USER]

    @classmethod
    def create(cls,
               data,
               id_=None,
               dbcommit=False,
               with_bucket=False,
               **kwargs):
        """Create a record and sync roles.

        :param data: Metadata for record.
        :param id_: Record UUID.
        :param dbcommit: True for validating transaction.
        :param with_bucket: True for associating a bucket to record.
        :returns: Created record instance.
        """
        record = super(UserRecord, cls).create(data, id_, dbcommit,
                                               with_bucket, **kwargs)

        record.sync_roles()
        return record

    def update(self, data):
        """Update data for record and update roles.

        :param data: New metadata of the record.
        :returns: Record instance.
        """
        super(UserRecord, self).update(data)
        self.sync_roles()
        return self

    def delete(self, force=False, dbcommit=True, delindex=False):
        """Delete record and persistent identifier.

        :param force: True to hard delete record.
        :param dbcommit: True for validating database transaction.
        :param delindex: True to remove record from index.
        """
        # Remove roles from user account.
        self.remove_roles()

        # Deactivate account.
        datastore.deactivate_user(self.user)

        return super(UserRecord, self).delete(force=force,
                                              dbcommit=dbcommit,
                                              delindex=delindex)

    @cached_property
    def user(self):
        """User account linked to current record.

        :returns: User account.
        """
        email = self.get('email')
        user = datastore.find_user(email=email)

        if not user:
            # Hash password before storing it.
            password = hash_password(email)

            # Create and save new user.
            user = datastore.create_user(email=email, password=password)
            datastore.commit()

            # Send password reset
            send_reset_password_instructions(user)

            # Directly confirm user (no account activation by email)
            confirm_user(user)
        else:
            # If user is not active, activate it.
            if not user.is_active:
                datastore.activate_user(user)

        return user

    def sync_roles(self):
        """Synchronize roles between record object and user account."""
        db_roles = self.user.roles

        for role in self.available_roles:
            in_db = role in db_roles
            in_record = role in self.get('roles', [])

            if in_record and not in_db:
                self.add_role_to_account(role)

            if not in_record and in_db:
                self.remove_role_from_account(role)

    def remove_roles(self):
        """Remove roles from user account."""
        db_roles = self.user.roles

        for role in self.available_roles:
            if role in db_roles:
                self.remove_role_from_account(role)

    @classmethod
    def get_user_by_current_user(cls, user):
        """Get user by current logged user."""
        return cls.get_user_by_email(email=user.email)

    @classmethod
    def get_user_by_email(cls, email):
        """Get patron by email."""
        pid_value = cls.get_pid_by_email(email)
        if pid_value:
            return cls.get_record_by_pid(pid_value)

        return None

    @classmethod
    def get_pid_by_email(cls, email):
        """Get uuid pid by email."""
        result = UserSearch().filter(
            'term', email=email).source(includes='pid').scan()
        try:
            return next(result).pid
        except StopIteration:
            return None

    @classmethod
    def get_reachable_roles(cls, role):
        """Get list of roles depending on role hierarchy."""
        if role not in UserRecord.ROLES_HIERARCHY:
            return []

        roles = UserRecord.ROLES_HIERARCHY[role].copy()
        roles.append(role)
        return roles

    @classmethod
    def get_all_roles_for_role(cls, role):
        """The list of roles covering given role based on the hierarchy."""
        roles = [role]
        for key in UserRecord.ROLES_HIERARCHY:
            if role in UserRecord.ROLES_HIERARCHY[key] and key not in roles:
                roles.append(key)

        return roles

    def add_role_to_account(self, role_name):
        """Add the given role to user account.

        :param role_name: Role to add.
        """
        role = datastore.find_role(role_name)
        datastore.add_role_to_user(self.user, role)
        datastore.commit()

    def remove_role_from_account(self, role_name):
        """Remove the given role from user account.

        :param role_name: Role to remove.
        """
        role = datastore.find_role(role_name)
        datastore.remove_role_from_user(self.user, role)
        datastore.commit()

    def get_moderators_emails(self):
        """Get the list of moderators emails."""
        organisation_pid = None

        if 'organisation' in self:
            organisation_pid = UserRecord.get_pid_by_ref_link(
                self['organisation']['$ref'])

        moderators = UserSearch().get_moderators(organisation_pid)

        return [result['email'] for result in moderators]

    def is_granted(self, role_to_check):
        """Check if user has at least the role passed in argument."""
        if 'roles' not in self:
            return False

        for role in self['roles']:
            if role_to_check in self.get_reachable_roles(role):
                return True

        return False

    @property
    def is_moderator(self):
        """Check if a user a moderator."""
        return self.is_granted(UserRecord.ROLE_MODERATOR)

    @property
    def is_user(self):
        """Check if a user a standard user."""
        return self.is_granted(UserRecord.ROLE_USER)

    @property
    def is_admin(self):
        """Check if a user an administrator."""
        return self.is_granted(UserRecord.ROLE_ADMIN)

    @property
    def is_super_admin(self):
        """Check if a user a super administrator."""
        return self.is_granted(UserRecord.ROLE_SUPERADMIN)


class UserIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = UserRecord
