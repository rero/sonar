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

"""JSON schema class."""

import copy
import re

from invenio_jsonschemas import current_jsonschemas

from sonar.modules.organisations.api import current_organisation
from sonar.modules.utils import has_custom_resource


class JSONSchemaBase:
    """Base class for managing JSON schemas."""

    _resource_type = None
    _schema = None

    def __init__(self, resource_type):
        """Class initialization.

        Stores the resource type and load the corresponding schema.

        :param resource_type: Type of resource
        """
        self._resource_type = resource_type
        self._load_schema()

    def _load_schema(self):
        """Process and return the JSON schema.

        :returns: The schema corresponding to the resource.
        """
        rec_type = self._resource_type
        rec_type = re.sub("ies$", "y", rec_type)
        rec_type = re.sub("s$", "", rec_type)

        current_jsonschemas.get_schema.cache_clear()
        schema_name = f"{self._resource_type}/{rec_type}-v1.0.0.json"

        if has_custom_resource(self._resource_type):
            schema_name = f'{current_organisation["code"]}/{schema_name}'

        self._schema = copy.deepcopy(current_jsonschemas.get_schema(schema_name))

    def get_schema(self):
        """Return the schema loaded.

        :returns: The loaded schema.
        """
        return self._schema

    def process(self):
        """Additional treatment for schema.

        :returns: The processed schema.
        """
        return self._schema
