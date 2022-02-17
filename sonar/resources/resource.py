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

"""Base Record resource."""

from invenio_records_resources.resources import \
    RecordResource as BaseRecordResource
from invenio_records_rest.utils import obj_or_import_string

from sonar.modules.organisations.api import current_organisation
from sonar.modules.utils import has_custom_resource


class RecordResource(BaseRecordResource):
    """Base record resource."""

    @property
    def config(self):
        """Get the configuration depending on the orgnanisation.

        :returns: Default configuration or the dedicated configuration.
        """
        if not hasattr(self.default_config, 'resource_name'):
            return self.default_config

        if not has_custom_resource(self.default_config.resource_name):
            return self.default_config

        resource_name = self.default_config.resource_name
        resource_config = (f'sonar.dedicated.{current_organisation["code"]}.'
                           f'{resource_name}.resource:RecordResourceConfig')

        return obj_or_import_string(resource_config)

    @config.setter
    def config(self, value):
        self.default_config = value
