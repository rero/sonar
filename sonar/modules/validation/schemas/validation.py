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

"""Validation schema."""

from marshmallow import Schema, fields, pre_load

from sonar.modules.api import SonarRecord
from sonar.modules.users.api import current_user_record
from sonar.modules.validation.api import Action, Status


class ValidationMetadataSchema(Schema):
    """Schema for validation metadata."""

    status = fields.Str()
    action = fields.Str()
    user = fields.Dict()
    comment = fields.Str()
    logs = fields.List(fields.Dict())


class ValidationSchemaMixin:
    """Validation schema."""

    validation = fields.Nested(ValidationMetadataSchema)

    @pre_load
    def add_validation_data(self, item, **kwargs):
        """Add validation data to record.

        :param item: Record item.
        :returns: The modified item.
        """
        if not item.get("validation"):
            item["validation"] = {"status": Status.IN_PROGRESS, "action": Action.SAVE}

        # Store user
        if not item["validation"].get("user"):
            item["validation"]["user"] = {"$ref": SonarRecord.get_ref_link("users", current_user_record["pid"])}

        return item
