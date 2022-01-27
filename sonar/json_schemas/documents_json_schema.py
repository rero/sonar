# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class DocumentsJSONSchema(JSONSchemaBase):
    """JSON schema for documents."""

    def process(self):
        """Documents JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        if not current_user_record:
            return schema

        # Get Organisation for the current logged user
        organisation = current_user_record.replace_refs()\
            .get('organisation', {})
        # Remove some fields on json for the shared organisation
        if not organisation.get('isDedicated', False):
            for field in [
                'collections', 'subdivisions', 'customField1',
                'customField2', 'customField3'
            ]:
                schema['properties'].pop(field, None)
                if field in schema.get('propertiesOrder', []):
                    schema['propertiesOrder'].remove(field)

        if not current_user_record.is_superuser:
            schema['properties'].pop('organisation', None)
            if 'organisation' in schema.get('propertiesOrder', []):
                schema['propertiesOrder'].remove('organisation')

        return schema
