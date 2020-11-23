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

"""Test BORIS record loader."""

from sonar.modules.documents.loaders.schemas.boris import BorisSchema


def test_boris_loader():
    """Test BORIS record loader."""
    xml = """
    <record>
        <metadata>
            <resource xsi:schemaLocation="http://namespace.openaire.eu/schema/oaire/ https://www.openaire.eu/schema/repo-lit/4.0/openaire.xsd">
                <oaire:resourceType resourceTypeGeneral="literature" uri="http://purl.org/coar/resource_type/c_6501">journal article</oaire:resourceType>
                <datacite:titles>
                    <datacite:title xml:lang="eng">Good Religion or Bad Religion</datacite:title>
                </datacite:titles>
                <datacite:creators>
                    <datacite:creator>
                        <datacite:creatorName>Plüss, David</datacite:creatorName>
                        <datacite:nameIdentifier nameIdentifierScheme="ORCID" schemeURI="http://orcid.org/">0000-0001-9368-4963</datacite:nameIdentifier>
                    </datacite:creator>
                    <datacite:creator>
                        <datacite:creatorName>Portmann, Adrian</datacite:creatorName>
                    </datacite:creator>
                </datacite:creators>
                <dc:format>application/pdf</dc:format>
                <dc:language>eng</dc:language>
                <oaire:file objectType="fulltext" mimeType="application/pdf" accessRightsURI="http://purl.org/coar/access_right/c_abf2">https://boris.unibe.ch/10713/1/Good%20religion%20or%20bad%20religion.%20Distanced%20church-members%20and%20their%20perception%20of%20religion%20and%20religious%20plurality.pdf</oaire:file>
                <datacite:rights rightsURI="http://purl.org/coar/access_right/c_abf2">open access</datacite:rights>
                <dc:publisher>Brill</dc:publisher>
                <datacite:date dateType="Issued">2011</datacite:date>
                <datacite:identifier identifierType="URL">https://boris.unibe.ch/10713/</datacite:identifier>
                <datacite:alternateIdentifiers>
                    <datacite:alternateIdentifier identifierType="DOI">10.7892/boris.10713</datacite:alternateIdentifier>
                    <datacite:alternateIdentifier identifierType="TEST">1223334444</datacite:alternateIdentifier>
                </datacite:alternateIdentifiers>
                <datacite:relatedIdentifiers>
                    <datacite:relatedIdentifier relationType="IsVersionOf" relatedIdentifierType="DOI">10.1163/157092511X604009</datacite:relatedIdentifier>
                    <datacite:relatedIdentifier relationType="IsVersionOf" relatedIdentifierType="PMID">123456</datacite:relatedIdentifier>
                    <datacite:relatedIdentifier relationType="IsPartOf" relatedIdentifierType="ISSN">0922-2936</datacite:relatedIdentifier>
                </datacite:relatedIdentifiers>
                <datacite:subjects>
                    <datacite:subject subjectScheme="DDC" schemeURI="http://dewey.info/">230 Christianity  Christian theology</datacite:subject>
                </datacite:subjects>
                <oaire:citationStartPage>180</oaire:citationStartPage>
                <oaire:citationEndPage>196</oaire:citationEndPage>
                <oaire:citationVolume>24</oaire:citationVolume>
                <oaire:citationIssue>2</oaire:citationIssue>
                <oaire:citationTitle>Journal of empirical theology JET</oaire:citationTitle>
            </resource>
        </metadata>
    </record>
    """  # nopep8
    assert BorisSchema().dump(xml) == {
        'title': [{
            'type':
            'bf:Title',
            'mainTitle': [{
                'value': 'Good Religion or Bad Religion',
                'language': 'eng'
            }]
        }],
        'identifiedBy': [{
            'type': 'bf:Local',
            'source': 'BORIS',
            'value': 'https://boris.unibe.ch/10713/'
        }, {
            'type': 'bf:Doi',
            'value': '10.7892/boris.10713'
        }, {
            'type': 'bf:Local',
            'source': 'PMID',
            'value': '123456'
        }]
    }

    # Not well structured
    xml = """
    <resource></resource>
    """
    assert BorisSchema().dump(xml) == {'identifiedBy': [], 'title': []}
