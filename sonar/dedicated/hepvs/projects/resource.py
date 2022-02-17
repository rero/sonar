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

"""HEP Valais Projects resource."""

from flask_resources import ResponseHandler
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources import \
    RecordResourceConfig as BaseRecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers

from sonar.dedicated.hepvs.projects.serializers.csv import CSVSerializer
from sonar.resources.projects.resource import \
    RecordResourceConfig as BaseRecordResourceConfig
from sonar.resources.resources.responses import StreamResponseHandler


class RecordResourceConfig(BaseRecordResourceConfig):
    """HEP Valais Projects resource configuration."""

    response_handlers = {
        'application/json': ResponseHandler(
            JSONSerializer(),
            headers=etag_headers),
        'text/csv': StreamResponseHandler(
            CSVSerializer(csv_included_fields=[
                'pid', 'name', 'approvalDate', 'projectSponsor', 'statusHep',
                'mainTeam', 'innerSearcher', 'secondaryTeam',
                'externalPartners', 'status', 'startDate', 'endDate',
                'description', 'keywords', 'realizationFramework',
                'funding_funder_type', 'funding_funder_name',
                'funding_funder_number', 'funding_fundingReceived',
                'actorsInvolved', 'benefits', 'impactOnFormation',
                'impactOnProfessionalEnvironment', 'impactOnPublicAction',
                'promoteInnovation', 'relatedToMandate_mandate',
                'relatedToMandate_name', 'relatedToMandate_briefDescription',
                'educationalDocument', 'searchResultsValorised'
            ]),
            filename='projects.csv',
            headers=etag_headers)
    }
