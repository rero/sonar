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

from marshmallow import fields

from sonar.resources.projects.schema import \
    MetadataSchema as BaseMetadataSchema
from sonar.resources.projects.schema import RecordSchema as BaseRecordSchema


class MetadataSchema(BaseMetadataSchema):
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
