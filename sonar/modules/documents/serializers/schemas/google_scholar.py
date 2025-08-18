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

"""Google scholar marshmallow schema."""

from __future__ import absolute_import, print_function, unicode_literals

from flask import request
from marshmallow import fields, post_dump

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.views import get_language_from_bibliographic_code

from .base_schema import BaseSchema


class GoogleScholarV1(BaseSchema):
    """Marshmallow schema for Google scholar."""

    title = fields.Method("get_title")
    language = fields.Method("get_language")
    publication_date = fields.Method("get_start_date")
    keywords = fields.Method("get_keywords")
    pdf_url = fields.Method("get_url")
    online_date = fields.Method("get_start_date")
    author = fields.Method("get_author")
    doi = fields.Method("get_doi")
    abstract_html_url = fields.Method("get_abstract_url")
    pages = fields.Method("get_pages")
    firstpage = fields.Method("get_first_page")
    lastpage = fields.Method("get_last_page")
    volume = fields.Method("get_volume")
    journal_title = fields.Method("get_host_document_title")

    def get_abstract_url(self, obj):
        """Get id."""
        return DocumentRecord.get_permanent_link(request.host_url, obj["metadata"]["pid"], ignore_ark=True)

    def get_language(self, obj):
        """Get language."""
        for language in obj["metadata"].get("language", []):
            return get_language_from_bibliographic_code(language["value"])

        return None

    def get_keywords(self, obj):
        """Get keywords."""
        return " ; ".join(super(GoogleScholarV1, self).get_keywords(obj))

    def get_author(self, obj):
        """Get authors."""
        items = []
        for contributor in obj["metadata"].get("contribution", []):
            if contributor["role"][0] == "cre" and contributor["agent"].get("preferred_name"):
                items.append(contributor["agent"]["preferred_name"])

        return items

    def get_doi(self, obj):
        """Get DOI."""
        for identifier in obj["metadata"].get("identifiedBy", []):
            if identifier["type"] == "bf:Doi":
                return identifier["value"]

        return None

    def get_volume(self, obj):
        """Get volume."""
        for part_of in obj["metadata"].get("partOf", []):
            if part_of.get("numberingVolume"):
                return part_of["numberingVolume"]

        return None

    def get_host_document_title(self, obj):
        """Get volume."""
        for part_of in obj["metadata"].get("partOf", []):
            if part_of.get("document", {}).get("title"):
                return part_of["document"]["title"]

        return None

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}
