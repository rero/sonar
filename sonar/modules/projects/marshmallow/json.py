# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Marshmallow schemas for projects."""

from __future__ import absolute_import, print_function

from functools import partial

from flask_security import current_user
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import GenFunction, \
    PersistentIdentifier, SanitizedUnicode
from marshmallow import fields, pre_dump, pre_load

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.projects.api import ProjectRecord
from sonar.modules.projects.permissions import ProjectPermission
from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record

schema_from_project = partial(schema_from_context, schema=ProjectRecord.schema)


class ProjectMetadataSchemaV1(StrictKeysMixin):
    """Schema for the project metadata."""

    pid = PersistentIdentifier()
    name = SanitizedUnicode(required=True)
    description = SanitizedUnicode()
    startDate = SanitizedUnicode()
    endDate = SanitizedUnicode()
    identifiedBy = fields.Dict()
    investigators = fields.List(fields.Dict())
    funding_organisations = fields.List(fields.Dict())
    organisation = fields.Dict()
    user = fields.Dict()
    documents = fields.List(fields.Dict(), dump_only=True)
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(load_only=True,
                         attribute="$schema",
                         data_key="$schema",
                         deserialize=schema_from_project)
    permissions = fields.Dict(dump_only=True)

    def dump(self, obj, *args, **kwargs):
        """Dump object.

        Override the parent method to add the documents linked to projects.
        It was not possible to use the `pre_dump` decorator, because
        `add_permission` need this property and we cannot be sure that this
        hook will be executed first.
        """
        obj['documents'] = DocumentRecord.get_documents_by_project(obj['pid'])
        return super(ProjectMetadataSchemaV1, self).dump(obj, *args, **kwargs)

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        item['permissions'] = {
            'read': ProjectPermission.read(current_user, item),
            'update': ProjectPermission.update(current_user, item),
            'delete': ProjectPermission.delete(current_user, item)
        }

        return item

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop('permissions', None)
        data.pop('documents', None)

        return data

    @pre_load
    def guess_organisation(self, data, **kwargs):
        """Guess organisation from current logged user.

        :param data: Dict of record data.
        :returns: Modified dict of record data.
        """
        # Organisation already attached to document, we do nothing.
        if data.get('organisation'):
            return data

        # Store current user organisation in new document.
        if current_user_record.get('organisation'):
            data['organisation'] = current_user_record['organisation']

        return data

    @pre_load
    def guess_user(self, data, **kwargs):
        """Guess user.

        :param data: Dict of record data.
        :returns: Modified dict of record data.
        """
        # If user is already set, we don't set it.
        if data.get('user'):
            return data

        # Store current user in project.
        data['user'] = {
            '$ref':
            current_user_record.get_ref_link('users',
                                             current_user_record['pid'])
        }

        return data


class ProjectSchemaV1(StrictKeysMixin):
    """Project schema."""

    metadata = fields.Nested(ProjectMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
