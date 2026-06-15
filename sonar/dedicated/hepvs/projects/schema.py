# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects schema."""

from marshmallow import fields

from sonar.modules.validation.schemas.validation import ValidationSchemaMixin
from sonar.resources.projects.schema import MetadataSchema as BaseMetadataSchema
from sonar.resources.projects.schema import RecordSchema as BaseRecordSchema


class MetadataSchema(BaseMetadataSchema, ValidationSchemaMixin):
    """Schema for the project metadata."""

    projectSponsor = fields.Str()
    approvalDate = fields.Str()
    statusHep = fields.Str()
    innerSearcher = fields.List(fields.Str())
    externalPartners = fields.Dict()
    mainTeam = fields.Str()
    secondaryTeam = fields.Str()
    status = fields.Str()
    keywords = fields.List(fields.Str())
    realizationFramework = fields.List(fields.Str())
    funding = fields.Dict()
    actorsInvolved = fields.List(fields.Dict())
    benefits = fields.Str()
    impactOnFormation = fields.Str()
    impactOnProfessionalEnvironment = fields.Str()
    impactOnPublicAction = fields.Str()
    promoteInnovation = fields.Dict()
    relatedToMandate = fields.Dict()
    educationalDocument = fields.Dict()
    searchResultsValorised = fields.Str()


class RecordSchema(BaseRecordSchema):
    """Schema for records v1 in JSON."""

    metadata = fields.Nested(MetadataSchema)
