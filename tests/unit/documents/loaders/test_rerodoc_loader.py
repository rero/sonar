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

from sonar.modules.documents.loaders.schemas.rerodoc import RerodocSchema


def test_rerodoc_loader(app, organisation):
    """Test RERODOC record loader."""
    xml = """
    <record xmlns="http://www.openarchives.org/OAI/2.0/"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <header>
            <identifier>oai:doc.rero.ch:289209</identifier>
            <datestamp>2017-08-02T19:31:33Z</datestamp>
            <setSpec>nl-uzh</setSpec>
            <setSpec>article</setSpec>
            <setSpec>rero_explore</setSpec>
            <setSpec>postprint</setSpec>
        </header>
        <metadata>
            <marc:record xmlns:marc="http://www.loc.gov/MARC21/slim"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" type="Bibliographic">
                <marc:leader>00000coc  2200000uu 4500</marc:leader>
                <marc:controlfield tag="001">289209</marc:controlfield>
                <marc:controlfield tag="005">20170803135013.0</marc:controlfield>
                <marc:datafield tag="024" ind1="7" ind2="0">
                    <marc:subfield code="a">10.1093/mnras/stu2500</marc:subfield>
                    <marc:subfield code="2">doi</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="024" ind1="8" ind2=" ">
                    <marc:subfield code="a">oai:doc.rero.ch:289209</marc:subfield>
                    <marc:subfield code="p">nl-uzh</marc:subfield>
                    <marc:subfield code="p">article</marc:subfield>
                    <marc:subfield code="p">rero_explore</marc:subfield>
                    <marc:subfield code="p">postprint</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="037" ind1=" " ind2=" ">
                    <marc:subfield code="a">swissbib.ch:(NATIONALLICENCE)oxford-10.1093/mnras/stu2500</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                    <marc:subfield code="a">eng</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="080" ind1=" " ind2=" ">
                    <marc:subfield code="a">52</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="100" ind1=" " ind2=" ">
                    <marc:subfield code="a">Capelo, Pedro R.</marc:subfield>
                    <marc:subfield code="u">Department of Astronomy, University of Michigan, Ann Arbor, MI 48109, USA</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="245" ind1=" " ind2=" ">
                    <marc:subfield code="a">Growth and activity of black holes in galaxy mergers with varying mass ratios</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="a">We study supermassive black holes (BHs) in merging galaxies</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="540" ind1=" " ind2=" ">
                    <marc:subfield code="a">© 2015 The Authors Published by Oxford University Press on behalf of the Royal Astronomical Society</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="695" ind1=" " ind2=" ">
                    <marc:subfield code="a">galaxies: active ; galaxies: interactions ; galaxies: nuclei</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Volonteri, Marta</marc:subfield>
                    <marc:subfield code="u">Department of Astronomy, University of Michigan, Ann Arbor, MI 48109, USA</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Dotti, Massimo</marc:subfield>
                    <marc:subfield code="u">Dipartimento di Fisica G. Occhialini, Università degli Studi di Milano Bicocca, Piazza della Scienza 3, I-20126 Milano, Italy</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Bellovary, Jillian M.</marc:subfield>
                    <marc:subfield code="u">Department of Physics and Astronomy, Vanderbilt University, Nashville, TN 37235, USA</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Mayer, Lucio</marc:subfield>
                    <marc:subfield code="u">Institute for Computational Science, University of Zürich, Winterthurerstrasse 190, CH-8057 Zürich, Switzerland</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Governato, Fabio</marc:subfield>
                    <marc:subfield code="u">Department of Astronomy, University of Washington, Box 351580, Seattle, WA 98195, USA</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="773" ind1=" " ind2=" ">
                    <marc:subfield code="x">0035-8711</marc:subfield>
                    <marc:subfield code="t">Monthly Notices of the Royal Astronomical Society</marc:subfield>
                    <marc:subfield code="g">2015/447/3/2123-2143</marc:subfield>
                    <marc:subfield code="d">Oxford University Press</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="775" ind1=" " ind2=" ">
                    <marc:subfield code="g">Publisher's version</marc:subfield>
                    <marc:subfield code="o">https://doi.org/10.1093/mnras/stu2500</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="919" ind1=" " ind2=" ">
                    <marc:subfield code="a">Consortium of Swiss Academic Libraries</marc:subfield>
                    <marc:subfield code="b">Zurich</marc:subfield>
                    <marc:subfield code="d">doc.support@rero.ch</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="980" ind1=" " ind2=" ">
                    <marc:subfield code="a">POSTPRINT</marc:subfield>
                    <marc:subfield code="b">org</marc:subfield>
                    <marc:subfield code="f">ART_JOURNAL</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="982" ind1=" " ind2=" ">
                    <marc:subfield code="a">National Licences: uzh</marc:subfield>
                </marc:datafield>
            </marc:record>
        </metadata>
    </record>
    """  # nopep8
    assert RerodocSchema().dump(xml) == {
        'identifiedBy': [{
            'type': 'bf:Local',
            'source': 'RERO DOC',
            'value': '289209'
        }, {
            'type':
            'bf:Local',
            'source':
            'Swissbib',
            'value':
            '(NATIONALLICENCE)oxford-10.1093/mnras/stu2500'
        }],
        'specificCollections': ['National Licences: uzh'],
        'usageAndAccessPolicy': {
            'label':
            '© 2015 The Authors Published by Oxford University Press on '
            'behalf of the Royal Astronomical Society',
            'license': 'Other OA / license undefined'
        },
        'abstracts': [{
            'value':
            'We study supermassive black holes (BHs) in merging galaxies',
            'language': 'eng'
        }],
        'partOf': [{
            'numberingYear': '2015',
            'numberingVolume': '447',
            'numberingIssue': '3',
            'numberingPages': '2123-2143',
            'document': {
                'title': 'Monthly Notices of the Royal Astronomical Society',
                'publication': {
                    'statement': 'Oxford University Press'
                }
            }
        }],
        'provisionActivity': [{
            'type': 'bf:Publication',
            'startDate': '2015'
        }],
        'otherEdition': [{
            'document': {
                'electronicLocator': 'https://doi.org/10.1093/mnras/stu2500'
            },
            'publicNote': "Publisher's version"
        }],
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }],
        'documentType':
        'coar:c_6501',
        'organisation': {
            '$ref': 'https://sonar.ch/api/organisations/org'
        },
        'classification': [{
            'type': 'bf:ClassificationUdc',
            'classificationPortion': '52'
        }],
        'contribution': [{
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Capelo, Pedro R.'
            },
            'role': ['cre'],
            'affiliation':
            'Department of Astronomy, University of Michigan, Ann Arbor, MI '
            '48109, USA'
        }, {
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Volonteri, Marta'
            },
            'role': ['cre'],
            'affiliation':
            'Department of Astronomy, University of Michigan, Ann Arbor, MI '
            '48109, USA'
        }, {
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Dotti, Massimo'
            },
            'role': ['cre'],
            'affiliation':
            'Dipartimento di Fisica G. Occhialini, Università degli Studi di '
            'Milano Bicocca, Piazza della Scienza 3, I-20126 Milano, Italy'
        }, {
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Bellovary, Jillian M.'
            },
            'role': ['cre'],
            'affiliation':
            'Department of Physics and Astronomy, Vanderbilt University, '
            'Nashville, TN 37235, USA'
        }, {
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Mayer, Lucio'
            },
            'role': ['cre'],
            'affiliation':
            'Institute for Computational Science, University of Zürich, '
            'Winterthurerstrasse 190, CH-8057 Zürich, Switzerland',
            'controlledAffiliation': ['Uni of Zurich and Hospital']
        }, {
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Governato, Fabio'
            },
            'role': ['cre'],
            'affiliation':
            'Department of Astronomy, University of Washington, Box 351580, '
            'Seattle, WA 98195, USA'
        }],
        'title': [{
            'type':
            'bf:Title',
            'mainTitle': [{
                'value':
                'Growth and activity of black holes in galaxy mergers with '
                'varying mass ratios',
                'language':
                'eng'
            }]
        }]
    }
