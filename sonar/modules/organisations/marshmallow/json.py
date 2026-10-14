# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""JSON Schemas."""

from functools import partial

from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    GenFunction,
    PersistentIdentifier,
    SanitizedUnicode,
)
from marshmallow import EXCLUDE, ValidationError, fields, pre_dump, pre_load, validate, validates
from marshmallow_utils.context import context_schema

from sonar.modules.organisations.api import OrganisationRecord, current_organisation
from sonar.modules.organisations.permissions import (
    OrganisationFilesPermission,
    OrganisationPermission,
)
from sonar.modules.permissions import has_superuser_access
from sonar.modules.serializers import schema_from_context
from sonar.modules.users.api import current_user_record

schema_from_organisation = partial(schema_from_context, schema=OrganisationRecord.schema)
THEME_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


class FileSchemaV1(StrictKeysMixin):
    """File schema."""

    class Meta:
        """Meta for file schema."""

        # Specifically exclude unknown fields, as in the new version of
        # marshmallow, dump_only fields are treated as included.
        # https://github.com/marshmallow-code/marshmallow/issues/875
        unknown = EXCLUDE

    bucket = SanitizedUnicode()
    file_id = SanitizedUnicode()
    version_id = SanitizedUnicode()
    key = fields.Str()
    mimetype = SanitizedUnicode()
    checksum = SanitizedUnicode()
    size = fields.Integer()
    label = SanitizedUnicode()
    type = SanitizedUnicode()
    order = fields.Integer()
    external_url = SanitizedUnicode()
    access = SanitizedUnicode()
    restricted_outside_organisation = fields.Boolean()
    embargo_date = SanitizedUnicode()
    restriction = fields.Dict(dump_only=True)
    links = fields.Dict(dump_only=True)
    thumbnail = SanitizedUnicode(dump_only=True)
    permissions = fields.Dict(dump_only=True)

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        if not item.get("bucket"):
            return item
        doc = OrganisationRecord.get_record_by_bucket(item.get("bucket"))
        item["permissions"] = {
            "read": OrganisationFilesPermission.read(current_user_record, item, doc["pid"], doc),
            "update": OrganisationFilesPermission.update(current_user_record, item, doc["pid"], doc),
            "delete": OrganisationFilesPermission.delete(current_user_record, item, doc["pid"], doc),
        }

        return item

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop("permissions", None)
        return data


class ThemeSchemaV1(StrictKeysMixin):
    """Organisation theme schema."""

    primaryColor = SanitizedUnicode(validate=validate.Regexp(THEME_COLOR_PATTERN))
    secondaryColor = SanitizedUnicode(validate=validate.Regexp(THEME_COLOR_PATTERN))
    css = fields.Str()

    @pre_load
    def normalize_colors(self, data, **kwargs):
        """Normalize hexadecimal colors before validation."""
        for key in ("primaryColor", "secondaryColor"):
            if isinstance(data.get(key), str):
                data[key] = data[key].strip().upper()
        return data

    @validates("css")
    def validate_css(self, value, **kwargs):
        """Reject CSS that could close the style tag of the page."""
        if "</" in value:
            raise ValidationError("CSS must not contain `</`.")


class OrganisationMetadataSchemaV1(StrictKeysMixin):
    """Schema for the organisation metadata."""

    pid = PersistentIdentifier()
    code = SanitizedUnicode(required=True)
    name = SanitizedUnicode(required=True)
    description = fields.List(fields.Dict())
    footer = fields.List(fields.Dict())
    isShared = fields.Boolean()
    isDedicated = fields.Boolean()
    theme = fields.Nested(ThemeSchemaV1)
    serverName = fields.Str()
    allowedIps = SanitizedUnicode()
    arkNAAN = SanitizedUnicode()
    platformName = SanitizedUnicode()
    documentsCustomField1 = fields.Dict()
    documentsCustomField2 = fields.Dict()
    documentsCustomField3 = fields.Dict()
    publicDocumentFacets = fields.List(fields.String())
    # When loading, if $schema is not provided, it's retrieved by
    # Record.schema property.
    schema = GenFunction(
        load_only=True,
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_organisation,
    )
    permissions = fields.Dict(dump_only=True)
    _files = Nested(FileSchemaV1, many=True)
    _bucket = SanitizedUnicode()

    @pre_dump
    def add_permissions(self, item, **kwargs):
        """Add permissions to record.

        :param item: Dict representing the record.
        :returns: Modified dict.
        """
        item["permissions"] = {
            "read": OrganisationPermission.read(current_user_record, item),
            "update": OrganisationPermission.update(current_user_record, item),
            "delete": OrganisationPermission.delete(current_user_record, item),
        }

        return item

    @pre_load
    def remove_fields(self, data, **kwargs):
        """Removes computed fields.

        :param data: Dict of record data.
        :returns: Modified data.
        """
        data.pop("permissions", None)

        return data

    @pre_load
    def override_modes(self, data, **kwargs):
        """Override organisation's modes.

        For non super users, the modes (isShared, isDedicated) is not saved
        by posting the data, but guessed from user's organisation.
        """
        if not has_superuser_access():
            data["isShared"] = current_organisation.get("isShared", False)
            data["isDedicated"] = current_organisation.get("isDedicated", False)
        return data

    @pre_load
    def override_ark_naan(self, data, **kwargs):
        """Override ARK naan.

        For non super users, the NAAN ark is not saved
        by posting the data, but guessed from user's organisation.
        """
        if not has_superuser_access():
            if ark_naan := current_organisation.get("arkNAAN"):
                data["arkNAAN"] = ark_naan
            else:
                data.pop("arkNAAN", None)
        return data

    @pre_load
    def keep_theme(self, data, **kwargs):
        """Keep the stored theme.

        The theme is only managed with the CLI, so the posted one is replaced
        by the one of the record being updated, which the loader puts in the
        context.
        """
        data.pop("theme", None)
        if (record := context_schema.get().get("record")) and (theme := record.get("theme")):
            data["theme"] = dict(theme)
        return data


class OrganisationSchemaV1(StrictKeysMixin):
    """organisation schema."""

    metadata = fields.Nested(OrganisationMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    explanation = fields.Raw(dump_only=True)
