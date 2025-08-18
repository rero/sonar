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
