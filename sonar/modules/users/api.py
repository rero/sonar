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

"""User Api."""

from functools import partial

from elasticsearch_dsl.query import Q
from flask import _request_ctx_stack, current_app, has_request_context
from flask_security import current_user
from flask_security.confirmable import confirm_user
from flask_security.utils import hash_password
from werkzeug.local import LocalProxy
from werkzeug.utils import cached_property

from sonar.modules.users.utils import send_welcome_email

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider


def get_current_user():
    """Return current user record from context."""
    if has_request_context() and not hasattr(_request_ctx_stack.top,
                                             'user_record'):
        ctx = _request_ctx_stack.top
        ctx.user_record = None if (
            current_user.is_anonymous) else UserRecord.get_user_by_email(
                email=current_user.email)

    return getattr(_request_ctx_stack.top, 'user_record', None)


current_user_record = LocalProxy(get_current_user)

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

    def get_moderators(self, organisation_pid=None, subdivision_pid=None):
        """Get moderators corresponding to organisation.

        If no organisation provided, return moderators not associated with
        organisations.

        :param organisation_pid: Organisation PID.
        :param subdivision_pid: Subdivision PID.
        :returns: List of results
        """
        must = []

        if organisation_pid:
            must.append(Q('term', organisation__pid=organisation_pid))

        if not subdivision_pid:
            must.append(
                Q('bool',
                  should=[
                      Q('term', role=UserRecord.ROLE_ADMIN),
                      Q('bool',
                        must=Q('term', role=UserRecord.ROLE_MODERATOR),
                        must_not=Q('exists', field='subdivision'))
                  ]))

        else:
            must.append(
                Q('bool',
                  should=[
                      Q('term', role=UserRecord.ROLE_ADMIN),
                      Q('bool',
                        must=[
                            Q('term', role=UserRecord.ROLE_MODERATOR),
                            Q('term', subdivision__pid=subdivision_pid)
                        ])
                  ]))

        return self.query('bool', filter=Q(
            'bool', must=must)).source(includes=['pid', 'email']).scan()


class UserRecord(SonarRecord):
    """User record class."""

    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_SUBMITTER = 'submitter'
    ROLE_ADMIN = 'admin'
    ROLE_SUPERUSER = 'superuser'

    ROLES_HIERARCHY = {
        ROLE_USER: [],
        ROLE_SUBMITTER: [ROLE_USER],
        ROLE_MODERATOR: [ROLE_SUBMITTER, ROLE_USER],
        ROLE_ADMIN: [ROLE_MODERATOR, ROLE_SUBMITTER, ROLE_USER],
        ROLE_SUPERUSER:
        [ROLE_ADMIN, ROLE_MODERATOR, ROLE_SUBMITTER, ROLE_USER],
    }

    minter = user_pid_minter
    fetcher = user_pid_fetcher
    provider = UserProvider
    schema = 'users/user-v1.0.0.json'
    available_roles = [
        ROLE_SUPERUSER, ROLE_ADMIN, ROLE_MODERATOR, ROLE_SUBMITTER, ROLE_USER
    ]

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

            # Send welcome email
            send_welcome_email(self, user)

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
            in_record = role == self.get('role', None)

            if in_record and not in_db:
                self.add_role_to_account(role)

            if not in_record and in_db:
                self.remove_role_from_account(role)
        # add user in any cases if does not exists
        if 'user' not in [r.name for r in self.user.roles]:
            self.add_role_to_account('user')


    def remove_roles(self):
        """Remove roles from user account."""
        db_roles = self.user.roles
        for role in self.available_roles:
            # keep the user role
            if role in db_roles and role != UserRecord.ROLE_USER:
                self.remove_role_from_account(role)

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

    def get_moderators_emails(self, subdivision_pid=None):
        """Get the list of moderators emails.

        :param subdivision_pid: PID of a subdivision.
        :returns: List of emails.
        :rtype: list
        """
        organisation_pid = None

        if 'organisation' in self:
            organisation_pid = UserRecord.get_pid_by_ref_link(
                self['organisation']['$ref'])

        moderators = UserSearch().get_moderators(organisation_pid,
                                                 subdivision_pid)

        return [result['email'] for result in moderators]

    def is_granted(self, role_to_check):
        """Check if user has at least the role passed in argument."""
        if not self.get('role'):
            return False

        if role_to_check in self.get_reachable_roles(self.get('role')):
            return True

        return False

    def get_all_reachable_roles(self):
        """Get list of roles depending on role hierarchy."""
        roles = self.get_reachable_roles(self.get('role'))
        return list(set(roles))

    @property
    def is_moderator(self):
        """Check if a user a moderator."""
        return self.is_granted(UserRecord.ROLE_MODERATOR)

    @property
    def is_submitter(self):
        """Check if a user a submitter."""
        return self.is_granted(UserRecord.ROLE_SUBMITTER)

    @property
    def is_user(self):
        """Check if a user a standard user."""
        return self.is_granted(UserRecord.ROLE_USER)

    @property
    def is_admin(self):
        """Check if a user an administrator."""
        return self.is_granted(UserRecord.ROLE_ADMIN)

    @property
    def is_superuser(self):
        """Check if a user a super administrator."""
        return self.is_granted(UserRecord.ROLE_SUPERUSER)


class UserIndexer(SonarIndexer):
    """Indexing documents in Elasticsearch."""

    record_cls = UserRecord
