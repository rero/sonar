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

"""Document serializers."""

from invenio_records_rest.serializers.response import (
    record_responsify,
    search_responsify,
)

from ..marshmallow import DocumentListSchemaV1, DocumentSchemaV1
from .dc import DublinCoreSerializer
from .google_scholar import SonarGoogleScholarSerializer
from .json import JSONSerializer
from .schemaorg import SonarSchemaOrgSerializer
from .schemas.google_scholar import GoogleScholarV1
from .schemas.schemaorg import SchemaOrgV1

# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(DocumentSchemaV1)
json_list_v1 = JSONSerializer(DocumentListSchemaV1)
#: schema.org serializer
schemaorg_v1 = SonarSchemaOrgSerializer(SchemaOrgV1, replace_refs=True)
#: google scholar serializer
google_scholar_v1 = SonarGoogleScholarSerializer(GoogleScholarV1, replace_refs=True)
from sonar.modules.documents.serializers.schemas.dc import DublinCoreSchema

dc_v1 = DublinCoreSerializer(DublinCoreSchema)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, "application/json")
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_list_v1, "application/json")

#: JSON record serializer for individual records.
dc_v1_response = record_responsify(dc_v1, "text/xml")
#: JSON record serializer for search results.
dc_v1_search = search_responsify(dc_v1, "text/xml")

__all__ = (
    "json_v1",
    "json_v1_response",
    "json_v1_search",
    "dc_v1_response",
    "dc_v1_search",
)
