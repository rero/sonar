# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Medline schema."""

import re

from sonar.heg.serializers.schemas.heg import HEGSchema
from sonar.modules.utils import remove_html


class MedlineSchema(HEGSchema):
    """Medline marshmallow schema."""

    def get_title(self, obj):
        """Get title."""
        if not obj.get("title"):
            obj["title"] = "Unknown title"

        return [
            {
                "type": "bf:Title",
                "mainTitle": [{"value": obj["title"], "language": obj["language"]}],
            }
        ]

    def get_identifiers(self, obj):
        """Get identifiers."""
        identifiers = super().get_identifiers(obj)

        if obj.get("pmid"):
            identifiers.append({"type": "bf:Local", "source": "PMID", "value": obj["pmid"]})

        return identifiers

    def get_abstracts(self, obj):
        """Get abstracts."""
        if not obj.get("abstract"):
            return None

        return [{"value": remove_html(obj["abstract"]), "language": obj["language"]}]

    def get_subjects(self, obj):
        """Get subjects."""
        subjects = [{"label": {"language": obj["language"], "value": [item]}} for item in obj.get("keywords", [])]

        for item in obj.get("mesh_terms", []):
            matches = re.match(r"^.*:(.*)$", item)
            subjects.append(
                {
                    "label": {"language": obj["language"], "value": [matches.group(1)]},
                    "source": "MeSH",
                }
            )

        return subjects

    def get_contribution(self, obj):
        """Get contribution."""
        contributors = []

        for index, item in enumerate(obj.get("authors", [])):
            if item:
                contributor = {
                    "agent": {"type": "bf:Person", "preferred_name": item},
                    "role": ["cre"],
                }

                if index < len(obj.get("affiliations", [])):
                    contributor["affiliation"] = obj["affiliations"][index]

                contributors.append(contributor)

        return contributors

    def get_provision_activity(self, obj):
        """Get provision activity."""
        if not obj.get("pubyear") and not obj.get("entrez_date"):
            return []

        provision_activity = {"type": "bf:Publication"}

        if obj.get("pubyear"):
            provision_activity["startDate"] = obj["pubyear"]

        if obj.get("entrez_date"):
            provision_activity["statement"] = [{"type": "Date", "label": [{"value": obj.get("entrez_date")}]}]

        return [provision_activity]

    def get_part_of(self, obj):
        """Get part of."""
        if not obj.get("journal"):
            return None

        return [{"numberingYear": obj["pubyear"], "document": {"title": obj["journal"]}}]
