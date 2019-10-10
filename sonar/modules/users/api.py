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

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
UserProvider = type(
    'UserProvider',
    (Provider,),
    dict(pid_type='user')
)
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


class UserRecord(SonarRecord):
    """User record class."""

    minter = user_pid_minter
    fetcher = user_pid_fetcher
    provider = UserProvider
    schema = 'user'

    @classmethod
    def get_user_by_current_user(cls, user):
        """Get patron by user."""
        if hasattr(user, 'email'):
            return cls.get_user_by_email(email=user.email)

        return None

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
            'term',
            email=email
        ).source(includes='pid').scan()
        try:
            return next(result).pid
        except StopIteration:
            return None
