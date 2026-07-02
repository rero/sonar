# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Document serializers."""

from sonar.modules.documents.serializers.response import record_responsify, search_responsify
from sonar.modules.documents.serializers.schemas.dc import DublinCoreSchema

from ..marshmallow import DocumentListSchemaV1, DocumentReroSchemaV1, DocumentSchemaV1
from .bibtex import BibTeXSerializer
from .dc import DublinCoreSerializer
from .google_scholar import SonarGoogleScholarSerializer
from .json import JSONSerializer
from .ris import RISSerializer
from .schemaorg import SonarSchemaOrgSerializer
from .schemas.google_scholar import GoogleScholarV1
from .schemas.schemaorg import SchemaOrgV1

# Serializers
# ===========
#: JSON serializer definition.
json_v1 = JSONSerializer(DocumentSchemaV1)
json_doc = JSONSerializer(DocumentReroSchemaV1)
json_list_v1 = JSONSerializer(DocumentListSchemaV1)
#: schema.org serializer
schemaorg_v1 = SonarSchemaOrgSerializer(SchemaOrgV1, replace_refs=True)
#: google scholar serializer
google_scholar_v1 = SonarGoogleScholarSerializer(GoogleScholarV1, replace_refs=True)

dc_v1 = DublinCoreSerializer(DublinCoreSchema)
bibtex_v1 = BibTeXSerializer()
ris_v1 = RISSerializer()

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, "application/json")
json_doc_response = record_responsify(json_doc, "application/rero+json")
#: JSON record serializer for search results.
json_v1_search = search_responsify(json_list_v1, "application/json")

#: JSON record serializer for individual records, downloaded as an attachment.
#: Uses a dedicated mimetype so it never shadows the plain application/json
#: response consumed by the UI on the same endpoint.
json_export_v1_response = record_responsify(json_v1, "application/export+json", extension=".json")
#: JSON record serializer for search results, downloaded as an attachment.
json_export_v1_search = search_responsify(json_list_v1, "application/export+json", extension=".json")

#: Dublin Core record serializer for individual records.
dc_v1_response = record_responsify(dc_v1, "text/xml", extension=".xml")
#: Dublin Core record serializer for search results.
dc_v1_search = search_responsify(dc_v1, "text/xml", extension=".xml")

#: BibTeX record serializer for individual records.
bibtex_v1_response = record_responsify(bibtex_v1, "application/x-bibtex", extension=".bib")
#: BibTeX record serializer for search results.
bibtex_v1_search = search_responsify(bibtex_v1, "application/x-bibtex", extension=".bib")

#: RIS record serializer for individual records.
ris_v1_response = record_responsify(ris_v1, "application/x-research-info-systems", extension=".ris")
#: RIS record serializer for search results.
ris_v1_search = search_responsify(ris_v1, "application/x-research-info-systems", extension=".ris")

__all__ = (
    "bibtex_v1_response",
    "bibtex_v1_search",
    "dc_v1_response",
    "dc_v1_search",
    "json_export_v1_response",
    "json_export_v1_search",
    "json_v1",
    "json_v1_response",
    "json_v1_search",
    "ris_v1_response",
    "ris_v1_search",
)
