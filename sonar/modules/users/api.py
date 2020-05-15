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
from flask_security import current_user
from werkzeug.local import LocalProxy

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

current_user_record = LocalProxy(lambda: UserRecord.get_user_by_current_user(
    current_user))

# provider
UserProvider = type('UserProvider', (Provider, ), dict(pid_type='user'))
# minter
user_pid_minter = partial(id_minter, provider=UserProvider)
# fetcher
user_pid_fetcher = partial(id_fetcher, provider=UserProvider)


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
    ROLE_PUBLISHER = 'publisher'
    ROLE_ADMIN = 'admin'
    ROLE_SUPERADMIN = 'superadmin'

    ROLES_HIERARCHY = {
        ROLE_USER: [],
        ROLE_PUBLISHER: [ROLE_USER],
        ROLE_MODERATOR: [ROLE_PUBLISHER, ROLE_USER],
        ROLE_ADMIN: [ROLE_MODERATOR, ROLE_USER],
        ROLE_SUPERADMIN: [ROLE_ADMIN, ROLE_MODERATOR, ROLE_USER],
    }

    minter = user_pid_minter
    fetcher = user_pid_fetcher
    provider = UserProvider
    schema = 'users/user-v1.0.0.json'

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

    def get_all_reachable_roles(self):
        """Get list of roles depending on role hierarchy."""
        roles = []
        for role in self['roles']:
            roles.extend(self.get_reachable_roles(role))

        return list(set(roles))

    @property
    def is_moderator(self):
        """Check if a user a moderator."""
        return self.is_granted(UserRecord.ROLE_MODERATOR)

    @property
    def is_publisher(self):
        """Check if a user a pulisher."""
        return self.is_granted(UserRecord.ROLE_PUBLISHER)

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
