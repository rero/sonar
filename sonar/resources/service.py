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

"""SONAR resources base service class."""

from flask_principal import Identity, Need, UserNeed
from invenio_records_resources.services.records import \
    RecordService as BaseRecordService


class RecordService(BaseRecordService):
    """SONAR resources base service class."""

    def create(self, identity, data, links_config=None):
        """Create a record.

        :param identity: Identity of user creating the record.
        :param data: Input data according to the data schema.
        """
        if not identity:
            identity = Identity(1)
            identity.provides.add(UserNeed(1))
            identity.provides.add(Need(method='system_role', value='any_user'))

        return super().create(identity, data, links_config)
