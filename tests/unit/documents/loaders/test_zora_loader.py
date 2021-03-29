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

"""Test ZORA record loader."""

import pytest

from sonar.modules.documents.loaders.schemas.zora import ZoraSchema


def test_title():
    """Test title."""
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record></marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {}

    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="245" ind1=" " ind2=" ">
                    <marc:subfield code="a">Art and design as linked data :</marc:subfield>
                    <marc:subfield code="b">the LODZ project (Linked Open Data Zurich)</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {
        'title': [{
            'mainTitle': [{
                'language': 'eng',
                'value': 'Art and design as linked data :'
            }],
            'subtitle': [{
                'language': 'eng',
                'value': 'the LODZ project (Linked Open Data Zurich)'
            }],
            'type':
            'bf:Title'
        }]
    }


def test_identifiers():
    """Test identifiers."""
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:controlfield tag="001">1972</marc:controlfield>
                <marc:datafield tag="024" ind1="7" ind2=" ">
                    <marc:subfield code="2">doi</marc:subfield>
                    <marc:subfield code="a">10.15291/libellarium.v9i2.256</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="024" ind1="7" ind2=" ">
                    <marc:subfield code="2">doi</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="024" ind1="7" ind2=" ">
                    <marc:subfield code="2">pmid</marc:subfield>
                    <marc:subfield code="a">2222</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="024" ind1="7" ind2=" ">
                    <marc:subfield code="2">UNKNOWN</marc:subfield>
                    <marc:subfield code="a">1111</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {
        'identifiedBy': [{
            'source': 'ZORA',
            'type': 'bf:Local',
            'value': '1972'
        }, {
            'type': 'bf:Doi',
            'value': '10.15291/libellarium.v9i2.256'
        }, {
            'type': 'bf:Local',
            'value': '2222',
            'source': 'PMID'
        }, {
            'type': 'bf:Identifier',
            'value': '1111'
        }]
    }


@pytest.mark.parametrize('type, value, result, dissertation', [
    (None, None, None, None),
    ('local', 'Herausgegebenes wissenschaftliches Werk', 'coar:c_2f33', None),
    ('local', 'Monografie', 'coar:c_2f33', None),
    ('local', 'Buchkapitel', 'coar:c_3248', None),
    ('local', 'Konferenzbeitrag', 'coar:c_5794', None),
    ('local', 'Artikel', 'coar:c_6501', None),
    ('local', 'Zeitungsartikel', 'coar:c_998f', None),
    ('gnd-content', 'Forschungsbericht', 'coar:c_18ws', None),
    ('gnd-content', 'Hochschulschrift', 'coar:c_db06', 'Dissertation'),
    ('gnd-content', 'Hochschulschrift', 'coar:c_bdcc', 'Masterarbeit'),
    ('gnd-content', 'Hochschulschrift', 'habilitation_thesis', 'Habilitation'),
    ('local', 'Working Paper', 'coar:c_8042', None),
    ('local', 'non-existing', 'coar:c_1843', None)
])
def test_document_type(type, value, result, dissertation):
    """Test document type."""
    if not type:
        # No 655
        xml = """
        <record>
            <metadata>
                <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <marc:record>
                    </marc:record>
                </marc:collection>
            </metadata>
        </record>
        """
        assert ZoraSchema().dump(xml) == {}

        # No 655$a
        xml = """
        <record>
            <metadata>
                <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <marc:record>
                        <marc:datafield tag="655" ind1=" " ind2=" ">
                        </marc:datafield>
                    </marc:record>
                </marc:collection>
            </metadata>
        </record>
        """
        assert ZoraSchema().dump(xml) == {}

        # No 655$2
        xml = """
        <record>
            <metadata>
                <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <marc:record>
                        <marc:datafield tag="655" ind1=" " ind2=" ">
                            <marc:subfield code="a">Doc type</marc:subfield>
                        </marc:datafield>
                    </marc:record>
                </marc:collection>
            </metadata>
        </record>
        """
        assert ZoraSchema().dump(xml) == {}

        return

    xml = f"""
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="502" ind1=" " ind2=" ">
                    <marc:subfield code="b">{dissertation}</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="655" ind1=" " ind2=" ">
                    <marc:subfield code="a">{value}</marc:subfield>
                    <marc:subfield code="2">{type}</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml)['documentType'] == result


def test_language():
    """Test language."""
    # No 041
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record></marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {}

    # No 041$a
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {}

    # One language
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                    <marc:subfield code="a">eng</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }]
    }

    # Multiple 041
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                    <marc:subfield code="a">eng</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                    <marc:subfield code="a">fre</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }, {
            'type': 'bf:Language',
            'value': 'fre'
        }]
    }

    # Multiple 041$a
    xml = """
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="041" ind1=" " ind2=" ">
                    <marc:subfield code="a">eng</marc:subfield>
                    <marc:subfield code="a">fre</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ZoraSchema().dump(xml) == {
        'language': [{
            'type': 'bf:Language',
            'value': 'eng'
        }, {
            'type': 'bf:Language',
            'value': 'fre'
        }]
    }


def test_abstracts():
    """Test abstracts."""
    # No 520
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record></marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # No 520$a
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="9">fre</subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # No language
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="a">La Convention relative</subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'abstracts': [{
            'language': 'eng',
            'value': 'La Convention relative'
        }]
    }

    # One abstracts
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="9">fre</subfield>
                    <marc:subfield code="a">La Convention relative</subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'abstracts': [{
            'language': 'fre',
            'value': 'La Convention relative'
        }]
    }

    # Multiple abstracts
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="9">fre</subfield>
                    <marc:subfield code="a">La Convention relative</subfield>
                </marc:datafield>
                <marc:datafield tag="520" ind1=" " ind2=" ">
                    <marc:subfield code="9">eng</subfield>
                    <marc:subfield code="a">The Convention</subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'abstracts': [{
            'language': 'fre',
            'value': 'La Convention relative'
        }, {
            'language': 'eng',
            'value': 'The Convention'
        }]
    }


def test_date():
    """Test Date."""
    # No 264$c
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # 264$c, but wrong format.
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="264" ind1=" " ind2=" ">
                    <marc:subfield code="c">wrong</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # 264$c OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="264" ind1=" " ind2=" ">
                    <marc:subfield code="c">2019</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'provisionActivity': [{
            'startDate': '2019',
            'type': 'bf:Publication'
        }]
    }


def test_dissertation():
    """Test dissertation."""
    # OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="502" ind1=" " ind2=" ">
                    <marc:subfield code="b">Dissertation degree</marc:subfield>
                    <marc:subfield code="c">Universität Zürich</marc:subfield>
                    <marc:subfield code="d">2007</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'dissertation': {
            'degree': 'Dissertation degree',
            'grantingInstitution': 'Universität Zürich',
            'date': '2007'
        }
    }

    # No 502
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # 502, but no $b
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="502" ind1=" " ind2=" ">
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}


def test_host_document():
    """Test host document."""
    # No 773
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # No 773$t
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="773" ind1=" " ind2=" "></marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # Not $g, no provision activity start date
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="773" ind1=" " ind2=" ">
                    <marc:subfield code="t">Host document</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {}

    # Not $g, with provision activity start date
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="264" ind1=" " ind2=" ">
                    <marc:subfield code="c">2019</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="773" ind1=" " ind2=" ">
                    <marc:subfield code="t">Host document</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'partOf': [{
            'document': {
                'title': 'Host document'
            },
            'numberingYear': '2019'
        }],
        'provisionActivity': [{
            'startDate': '2019',
            'type': 'bf:Publication'
        }]
    }

    # OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="773" ind1=" " ind2=" ">
                    <marc:subfield code="t">Host document</marc:subfield>
                    <marc:subfield code="g">Bd. 16, Nr. 3, S. 411-413 (2002)</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ZoraSchema().dump(xml) == {
        'partOf': [{
            'document': {
                'title': 'Host document'
            },
            'numberingYear': '2002',
            'numberingVolume': '16',
            'numberingIssue': '3',
            'numberingPages': '411-413'
        }]
    }


def test_contribution_from_field_100():
    """Test extracting contribution from field 100."""
    # OK
    xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="e">VerfasserIn</subfield>
            <subfield code="4">aut</subfield>
            <subfield code="0">(orcid)0000-0003-3669-3497</subfield>
        </datafield>
    </record>
    """
    data = ZoraSchema().dump(xml)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'identifiedBy': {
                'type': 'bf:Local',
                'source': 'ORCID',
                'value': '0000-0003-3669-3497'
            }
        },
        'role': ['cre']
    }]

    # Not $a
    xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    data = ZoraSchema().dump(xml)
    assert not data.get('contribution')


def test_contribution_from_field_700():
    """Test extracting contribution from field 700."""
    # OK, with bad ORCID
    xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="e">AkademischeR BetreuerIn</subfield>
            <subfield code="4">dgs</subfield>
            <subfield code="0">non-orcid</subfield>
        </datafield>
    </record>
    """
    data = ZoraSchema().dump(xml)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea'
        },
        'role': ['dgs']
    }]

    # Not $a
    xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    data = ZoraSchema().dump(xml)
    assert not data.get('contribution')
