# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""JSON schema class."""

import copy
import re

from invenio_jsonschemas import current_jsonschemas
from invenio_jsonschemas.errors import JSONSchemaNotFound

from sonar.modules.organisations.api import current_organisation


class JSONSchemaBase:
    """Base class for managing JSON schemas."""

    _resource_type = None
    _schema = None
    _with_refs = False

    def __init__(self, resource_type, with_refs=False):
        """Class initialization.

        Stores the resource type and load the corresponding schema.

        :param resource_type: Type of resource
        """
        self._resource_type = resource_type
        self._with_refs = with_refs
        self._load_schema()

    def _load_schema(self):
        """Process and return the JSON schema.

        :returns: The schema corresponding to the resource.
        """
        rec_type = self._resource_type
        rec_type = re.sub("ies$", "y", rec_type)
        rec_type = re.sub("s$", "", rec_type)

        current_jsonschemas.get_schema.cache_clear()
        try:
            schema_path = f"{self._resource_type}/{rec_type}-v1.0.0.json"
            self._schema = copy.deepcopy(
                current_jsonschemas.get_schema(
                    f"{current_organisation.get('code')}/{schema_path}", with_refs=self._with_refs
                )
            )
        except JSONSchemaNotFound, AttributeError:
            self._schema = copy.deepcopy(current_jsonschemas.get_schema(schema_path, with_refs=self._with_refs))

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
