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

"""Documents JSON schema class."""

from sonar.modules.organisations.api import current_organisation
from sonar.modules.utils import get_language_value

from .json_schema_base import JSONSchemaBase


class DocumentsJSONSchema(JSONSchemaBase):
    """JSON schema for documents."""

    def process(self):
        """Document JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        # Change the label for field, depending on configuration in
        # organisation.
        for i in range(1, 4):
            # Not dedicated, the custom fields are removed
            if not current_organisation or not current_organisation.get(
                    'isDedicated'):
                schema['properties'].pop(f'customField{i}', None)
                schema['propertiesOrder'].remove(f'customField{i}')
            else:
                if schema['properties'].get(
                        f'customField{i}'
                ) and current_organisation and current_organisation.get(
                        f'documentsCustomField{i}', {}).get('label'):
                    schema['properties'][f'customField{i}'][
                        'title'] = get_language_value(
                            current_organisation[f'documentsCustomField{i}']
                            ['label'])

        return schema
