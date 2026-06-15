# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HEG schema."""

from marshmallow import Schema, fields, post_dump, pre_dump

from sonar.modules.utils import get_bibliographic_code_from_language


class HEGSchema(Schema):
    """HEG common marshmallow schema."""

    title = fields.Method("get_title")
    abstracts = fields.Method("get_abstracts")
    language = fields.Method("get_language")
    identifiedBy = fields.Method("get_identifiers")
    documentType = fields.Method("get_document_type")
    subjects = fields.Method("get_subjects")
    contribution = fields.Method("get_contribution")
    provisionActivity = fields.Method("get_provision_activity")
    partOf = fields.Method("get_part_of")

    @pre_dump
    def pre_process_record(self, item, **kwargs):
        """Pre-process record, before dumping."""
        # Store language
        if item.get("language"):
            language = item["language"]

            item["language"] = get_bibliographic_code_from_language(language)
        else:
            item["language"] = "eng"

        return item

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}

    def get_title(self, obj):
        """Get title."""
        return

    def get_abstracts(self, obj):
        """Get abstracts."""
        return

    def get_language(self, obj):
        """Get language."""
        return [{"type": "bf:Language", "value": obj["language"]}]

    def get_identifiers(self, obj):
        """Get identifiers."""
        return [{"type": "bf:Doi", "value": obj["_id"]}]

    def get_document_type(self, obj):
        """Get document type."""
        return "coar:c_6501"

    def get_subjects(self, obj):
        """Get subjects."""
        return

    def get_contribution(self, obj):
        """Get contribution."""
        return

    def get_provision_activity(self, obj):
        """Get provision activity."""
        return

    def get_part_of(self, obj):
        """Get part of."""
        return
