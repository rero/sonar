# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Openaire schema."""

import xmltodict
from dojson.utils import force_list
from marshmallow import Schema, fields, pre_dump


class OpenaireSchema(Schema):
    """Openaire marshmallow schema."""

    identifiedBy = fields.Method("get_identifiers")
    title = fields.Method("get_title")

    @pre_dump
    def parse_xml(self, data, **kwargs):
        """Parse xml data and convert into OrderedDict.

        :param data: XML string.
        :returns: OrderedDict.
        """
        result = xmltodict.parse(data)

        if not result.get("record", {}).get("metadata", {}).get("resource"):
            return {}

        return result["record"]["metadata"]["resource"]

    def get_identifiers(self, obj):
        """Create identifiers."""
        identifiers = []

        # Main identifier
        if obj.get("datacite:identifier"):
            identifiers.append(
                {
                    "type": "bf:Local",
                    "source": "BORIS",
                    "value": obj["datacite:identifier"]["#text"],
                }
            )

        # DOI
        if obj.get("datacite:alternateIdentifiers"):
            identifiers.extend(
                {"type": "bf:Doi", "value": identifier["#text"]}
                for identifier in force_list(obj["datacite:alternateIdentifiers"]["datacite:alternateIdentifier"])
                if identifier["@identifierType"] == "DOI"
            )

        # PMID
        if obj.get("datacite:relatedIdentifiers"):
            identifiers.extend(
                {
                    "type": "bf:Local",
                    "source": "PMID",
                    "value": identifier["#text"],
                }
                for identifier in force_list(obj["datacite:relatedIdentifiers"]["datacite:relatedIdentifier"])
                if identifier["@relationType"] == "IsVersionOf" and identifier["@relatedIdentifierType"] == "PMID"
            )

        return identifiers

    def get_title(self, obj):
        """Get title."""
        return [
            {
                "type": "bf:Title",
                "mainTitle": [
                    {
                        "value": title["#text"],
                        "language": title.get("@xml:lang", "eng"),
                    }
                ],
            }
            for title in force_list(obj.get("datacite:titles", {}).get("datacite:title", []))
        ]
