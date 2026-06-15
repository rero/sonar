# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Schema for exporting records."""

from marshmallow import Schema, fields


class ExportSchemaV1(Schema):
    """Schema for exporting records."""

    first_name = fields.String(dump_only=True)
    last_name = fields.String(dump_only=True)
    birth_date = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    street = fields.String(dump_only=True)
    postal_code = fields.String(dump_only=True)
    city = fields.String(dump_only=True)
    phone = fields.String(dump_only=True)
    organisation = fields.Dict(dump_only=True)
    role = fields.String(dump_only=True)
    password = fields.Method("get_password", dump_only=True)

    def get_password(self, obj):
        """Get hashed password."""
        return obj.user.password
