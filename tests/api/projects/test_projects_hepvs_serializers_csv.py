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

"""Test HEP Valais projects CSV serializer."""

import copy

from sonar.dedicated.hepvs.projects.serializers.csv import CSVSerializer


def test_serializer(app):
    """Test serializer."""
    csv = CSVSerializer(
        csv_included_fields=[
            "pid",
            "name",
            "approvalDate",
            "projectSponsor",
            "statusHep",
            "mainTeam",
            "innerSearcher",
            "secondaryTeam",
            "externalPartners",
            "status",
            "startDate",
            "endDate",
            "description",
            "keywords",
            "realizationFramework",
            "funding_funder_type",
            "funding_funder_name",
            "funding_funder_number",
            "funding_fundingReceived",
            "actorsInvolved",
            "benefits",
            "impactOnFormation",
            "impactOnProfessionalEnvironment",
            "impactOnPublicAction",
            "promoteInnovation",
            "relatedToMandate_mandate",
            "relatedToMandate_name",
            "relatedToMandate_briefDescription",
            "educationalDocument",
            "searchResultsValorised",
        ]
    )

    records = {
        "hits": {
            "hits": [
                {
                    "id": "1",
                    "metadata": {
                        "statusHep": "Lecturer/professor",
                        "searchResultsValorised": "Results used",
                        "funding": {
                            "choice": True,
                            "funder": {
                                "type": "​Swiss National Science Foundation",
                                "number": "1111",
                            },
                            "fundingReceived": True,
                        },
                        "impactOnFormation": "Benefits of research",
                        "approvalDate": "2021-05-10",
                        "innerSearcher": ["John Doe"],
                        "mainTeam": "Education, childhood and the learning Society 21",
                        "startDate": "2021-05-11",
                        "promoteInnovation": {"choice": True, "reason": "Because"},
                        "impactOnProfessionalEnvironment": "Impact of the research",
                        "realizationFramework": [
                            "Master of Advanced Studies",
                            "CAS or DAS",
                        ],
                        "status": "In progress",
                        "relatedToMandate": {
                            "name": "Bern",
                            "choice": True,
                            "mandate": "Other locality (Switzerland)",
                            "briefDescription": "Description of the mandate",
                        },
                        "endDate": "2021-05-28",
                        "educationalDocument": {
                            "choice": True,
                            "briefDescription": "Description of the report",
                        },
                        "description": "Summary",
                        "keywords": ["Test"],
                        "name": "Project title",
                        "benefits": "Benefits in the research",
                        "externalPartners": {
                            "list": [
                                {
                                    "institution": "RERO",
                                    "searcherName": "External partner",
                                }
                            ],
                            "choice": True,
                        },
                        "actorsInvolved": [{"count": 2, "choice": "Apprentice"}],
                        "impactOnPublicAction": "Impact of the research",
                        "projectSponsor": "Sébastien Délèze",
                        "secondaryTeam": "Education, childhood and the learning Society 21",
                    },
                }
            ]
        }
    }

    result = "".join(csv.serialize_object_list(copy.deepcopy(records)))
    assert result == (
        '"pid";"name";"approvalDate";"projectSponsor";"statusHep";"mainTeam";"innerSearcher";"secondaryTeam";"externalPartners";"status";"startDate";"endDate";"description";"keywords";"realizationFramework";"funding_funder_type";"funding_funder_name";"funding_funder_number";"funding_fundingReceived";"actorsInvolved";"benefits";"impactOnFormation";"impactOnProfessionalEnvironment";"impactOnPublicAction";"promoteInnovation";"relatedToMandate_mandate";"relatedToMandate_name";"relatedToMandate_briefDescription";"educationalDocument";"searchResultsValorised"\r\n'
        '"1";"Project title";"2021-05-10";"Sébastien Délèze";"Lecturer/professor";"Education, childhood and the learning Society 21";"John Doe";"Education, childhood and the learning Society 21";"External partner (RERO)";"In progress";"2021-05-11";"2021-05-28";"Summary";"Test";"Master of Advanced Studies|CAS or DAS";"​Swiss National Science Foundation";"";"1111";"True";"Apprentice (2)";"Benefits in the research";"Benefits of research";"Impact of the research";"Impact of the research";"Because";"Other locality (Switzerland)";"Bern";"Description of the mandate";"Description of the report";"Results used"\r\n'
    )

    records["hits"]["hits"][0]["metadata"]["funding"]["choice"] = False
    records["hits"]["hits"][0]["metadata"]["promoteInnovation"]["choice"] = False
    records["hits"]["hits"][0]["metadata"]["relatedToMandate"]["choice"] = False
    records["hits"]["hits"][0]["metadata"]["educationalDocument"]["choice"] = False
    records["hits"]["hits"][0]["metadata"]["externalPartners"]["choice"] = False

    result = "".join(csv.serialize_object_list(copy.deepcopy(records)))
    assert result == (
        '"pid";"name";"approvalDate";"projectSponsor";"statusHep";"mainTeam";"innerSearcher";"secondaryTeam";"externalPartners";"status";"startDate";"endDate";"description";"keywords";"realizationFramework";"funding_funder_type";"funding_funder_name";"funding_funder_number";"funding_fundingReceived";"actorsInvolved";"benefits";"impactOnFormation";"impactOnProfessionalEnvironment";"impactOnPublicAction";"promoteInnovation";"relatedToMandate_mandate";"relatedToMandate_name";"relatedToMandate_briefDescription";"educationalDocument";"searchResultsValorised"\r\n'
        '"1";"Project title";"2021-05-10";"Sébastien Délèze";"Lecturer/professor";"Education, childhood and the learning Society 21";"John Doe";"Education, childhood and the learning Society 21";"";"In progress";"2021-05-11";"2021-05-28";"Summary";"Test";"Master of Advanced Studies|CAS or DAS";"";"";"";"";"Apprentice (2)";"Benefits in the research";"Benefits of research";"Impact of the research";"Impact of the research";"";"";"";"";"";"Results used"\r\n'
    )
