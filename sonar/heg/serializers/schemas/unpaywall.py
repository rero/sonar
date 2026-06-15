# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Unpaywall schema."""

from marshmallow import Schema, fields, post_dump


class UnpaywallSchema(Schema):
    """Unpaywall marshmallow schema."""

    files = fields.Method("get_files")
    oa_status = fields.Method("get_oa_status")

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}

    def get_files(self, obj):
        """Get files."""
        if not obj.get("best_oa_location") or not obj["best_oa_location"].get("url_for_pdf"):
            return []

        return [
            {
                "key": "fulltext.pdf",
                "url": obj["best_oa_location"]["url_for_pdf"],
                "force_external_url": True,
                "label": "Full-text",
                "type": "file",
                "order": 0,
            }
        ]

    def get_oa_status(self, obj):
        """Get open access status."""
        return obj.get("oa_status")
