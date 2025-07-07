# -*- coding: utf-8 -*-
#
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

"""Projects schema."""

from flask import g
from flask_principal import AnonymousIdentity
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields, pre_dump, pre_load

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.users.api import current_user_record
from sonar.modules.validation.schemas.validation import ValidationSchemaMixin
from sonar.proxies import sonar


class MetadataSchema(Schema, ValidationSchemaMixin):
    """Schema for the project metadata."""

    name = fields.Str(required=True)
    description = fields.Str()
    startDate = fields.Str()
    endDate = fields.Str()
    identifiedBy = fields.Dict()
    investigators = fields.List(fields.Dict())
    funding_organisations = fields.List(fields.Dict())
    organisation = fields.Dict()
    user = fields.Dict()
    documents = fields.List(fields.Dict(), dump_only=True)
    permissions = fields.Dict(dump_only=True)

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop("permissions", None)
        data.pop("documents", None)

        return data

    @pre_load
    def guess_organisation(self, data, **kwargs):
        """Guess organisation from current logged user.

        :param data: Dict of record data.
        :returns: Modified dict of record data.
        """
        # Organisation already attached to project, we do nothing.
        if data.get("organisation"):
            return data

        # Store current user organisation in new project.
        if current_user_record.get("organisation"):
            data["organisation"] = current_user_record["organisation"]

        return data

    @pre_load
    def guess_user(self, data, **kwargs):
        """Guess user.

        :param data: Dict of record data.
        :returns: Modified dict of record data.
        """
        # If user is already set, we don't set it.
        if data.get("user") or not current_user_record:
            return data

        # Store current user in project.
        data["user"] = {
            "$ref": current_user_record.get_ref_link(
                "users", current_user_record["pid"]
            )
        }

        return data


class RecordSchema(BaseRecordSchema):
    """Schema for records v1 in JSON."""

    metadata = fields.Nested(MetadataSchema)

    def dump(self, obj, *args, **kwargs):
        """Dump object.

        Override the parent method to add the documents linked to projects.
        It was not possible to use the `pre_dump` decorator, because
        `add_permission` need this property and we cannot be sure that this
        hook will be executed first.
        """
        obj["metadata"]["documents"] = DocumentRecord.get_documents_by_project(
            obj["id"]
        )
        return super().dump(obj, *args, **kwargs)

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        service = sonar.service("projects")
        identity = g.get("identity", AnonymousIdentity())

        item["metadata"]["permissions"] = {
            "read": service.permission_policy("read", **{"record": item}).allows(
                identity
            ),
            "update": service.permission_policy("update", **{"record": item}).allows(
                identity
            ),
            "delete": service.permission_policy("delete", **{"record": item}).allows(
                identity
            ),
        }

        return item
