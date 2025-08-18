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

"""Crossref schema."""

import re

from sonar.heg.serializers.schemas.heg import HEGSchema
from sonar.modules.utils import remove_html


class CrossrefSchema(HEGSchema):
    """Crossref marshmallow schema."""

    def get_title(self, obj):
        """Get title."""
        titles = []

        for title in obj.get("title", []):
            titles.append(
                {
                    "type": "bf:Title",
                    "mainTitle": [{"value": title, "language": obj["language"]}],
                }
            )

        return titles

    def get_identifiers(self, obj):
        """Get identifiers."""
        identifiers = super(CrossrefSchema, self).get_identifiers(obj)

        if obj.get("ISSN"):
            identifiers.append({"type": "bf:Issn", "value": obj["ISSN"][0]})

        return identifiers

    def get_abstracts(self, obj):
        """Get abstracts."""
        if not obj.get("abstract"):
            return None

        return [{"value": remove_html(obj["abstract"]), "language": obj["language"]}]

    def get_subjects(self, obj):
        """Get subjects."""
        return [{"label": {"language": obj["language"], "value": [item]}} for item in obj.get("subject", [])]

    def get_contribution(self, obj):
        """Get contribution."""
        contributors = []

        for item in obj.get("author", []):
            if not item.get("given"):
                continue

            contributor = {
                "agent": {
                    "type": "bf:Person",
                    "preferred_name": f"{item['family']}, {item['given']}",
                },
                "role": ["cre"],
            }

            if item.get("affiliation"):
                contributor["affiliation"] = item["affiliation"][-1]["name"]

            if item.get("ORCID"):
                matches = re.match(r".*\/(.*)$", item["ORCID"])
                if matches:
                    contributor["agent"]["identifiedBy"] = {
                        "type": "bf:Local",
                        "source": "ORCID",
                        "value": matches.group(1),
                    }

            contributors.append(contributor)

        return contributors

    def get_provision_activity(self, obj):
        """Get provision activity."""
        if not obj.get("published-online"):
            return None

        date_parts = obj["published-online"]["date-parts"][0]
        provision_activity = {
            "type": "bf:Publication",
            "startDate": str(date_parts[0]),
            "statement": [
                {
                    "type": "Date",
                    "label": [{"value": "-".join(str(value) for value in date_parts)}],
                }
            ],
        }

        return [provision_activity]

    def get_part_of(self, obj):
        """Get part of."""
        if not obj.get("container-title"):
            return None

        date_parts = obj["issued"]["date-parts"][0]

        part_of = {
            "numberingYear": str(date_parts[0]),
            "document": {
                "title": obj["container-title"][0],
                "publication": {
                    "startDate": "-".join(str(value) for value in date_parts),
                    "statement": obj["publisher"],
                },
            },
        }

        if obj.get("volume"):
            part_of["numberingVolume"] = obj["volume"]

        if obj.get("journal-issue"):
            part_of["numberingIssue"] = obj["journal-issue"]["issue"]

        if obj.get("page"):
            part_of["numberingPages"] = obj["page"]

        # Add ISSN of the journal
        for issn_type in obj.get("issn-type", []):
            if issn_type["type"] == "electronic":
                part_of["document"]["identifiedBy"] = [{"type": "bf:Issn", "value": issn_type["value"]}]

        return [part_of]
