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

"""Test ArODES record loader."""

import pytest

from sonar.modules.documents.loaders.schemas.arodes import ArodesSchema


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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {
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
                    <marc:subfield code="2">DOI</marc:subfield>
                    <marc:subfield code="a">10.15291/libellarium.v9i2.256</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="024" ind1="7" ind2=" ">
                    <marc:subfield code="2">DOI</marc:subfield>
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
    assert ArodesSchema().dump(xml) == {
        'identifiedBy': [
            {
                'source': 'ArODES',
                'type': 'bf:Local',
                'value': '1972'
            },
            {
                'type': 'bf:Doi',
                'value': '10.15291/libellarium.v9i2.256'
            },
        ]
    }


@pytest.mark.parametrize('document_type,result',
                         [(None, None), ('other', 'coar:c_1843'),
                          ('livre', 'coar:c_2f33'),
                          ('chapitre', 'coar:c_3248'),
                          ('conference', 'coar:c_5794'),
                          ('scientifique', 'coar:c_6501'),
                          ('professionnel', 'coar:c_3e5a'),
                          ('rapport', 'coar:c_18ws'),
                          ('THESES', 'coar:c_db06'),
                          ('non-existing', 'coar:c_1843')])
def test_document_type(document_type, result):
    """Test document type."""
    if not document_type:
        # No 980
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
        assert ArodesSchema().dump(xml) == {}

        # No 980$a
        xml = """
        <record>
            <metadata>
                <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <marc:record>
                        <marc:datafield tag="980" ind1=" " ind2=" ">
                        </marc:datafield>
                    </marc:record>
                </marc:collection>
            </metadata>
        </record>
        """
        assert ArodesSchema().dump(xml) == {}

        return

    xml = f"""
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="980" ind1=" " ind2=" ">
                    <marc:subfield code="a">{document_type}</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    """
    assert ArodesSchema().dump(xml) == {'documentType': result}


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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {
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
    assert ArodesSchema().dump(xml) == {
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
    assert ArodesSchema().dump(xml) == {
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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {
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
    assert ArodesSchema().dump(xml) == {
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
    assert ArodesSchema().dump(xml) == {
        'abstracts': [{
            'language': 'fre',
            'value': 'La Convention relative'
        }, {
            'language': 'eng',
            'value': 'The Convention'
        }]
    }


def test_oa_status():
    """Test OA status."""
    # No 906
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
    assert ArodesSchema().dump(xml) == {}

    # No 906$a
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="906" ind1=" " ind2=" "></marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # Value NONE
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="906" ind1=" " ind2=" ">
                    <marc:subfield code="a">NONE</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="906" ind1=" " ind2=" ">
                    <marc:subfield code="a">GOLD</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {'oa_status': 'gold'}


def test_date():
    """Test Date."""
    # No 269$a, no 260$c
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
    assert ArodesSchema().dump(xml) == {}

    # 269, but no $a
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="269" ind1=" " ind2=" ">
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # 269$a, but wrong format.
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="269" ind1=" " ind2=" ">
                    <marc:subfield code="a">wrong</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # 269$a OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="269" ind1=" " ind2=" ">
                    <marc:subfield code="a">2019-01</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'provisionActivity': [{
            'startDate': '2019-01-01',
            'type': 'bf:Publication'
        }]
    }

    # 260, but no $c
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="260" ind1=" " ind2=" ">
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # 260$c, but wrong format.
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="260" ind1=" " ind2=" ">
                    <marc:subfield code="c">wrong</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # 260$c OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="260" ind1=" " ind2=" ">
                    <marc:subfield code="c">2019-01</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'provisionActivity': [{
            'startDate': '2019-01-01',
            'type': 'bf:Publication'
        }]
    }

    # 269$a and 260$c, 269 have priority
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="260" ind1=" " ind2=" ">
                    <marc:subfield code="c">2020-01</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="269" ind1=" " ind2=" ">
                    <marc:subfield code="a">2019-01</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'provisionActivity': [{
            'startDate': '2019-01-01',
            'type': 'bf:Publication'
        }]
    }


def test_subjects():
    """Test subjects."""
    # No 653
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
    assert ArodesSchema().dump(xml) == {}

    # 653 but not $a
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # OK, but no language --> default language `eng`
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                    <marc:subfield code="a">subject 1</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'subjects': [{
            'label': {
                'language': 'eng',
                'value': ['subject 1']
            }
        }]
    }

    # OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                    <marc:subfield code="a">sujet 1</marc:subfield>
                    <marc:subfield code="9">fre</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'subjects': [{
            'label': {
                'language': 'fre',
                'value': ['sujet 1']
            }
        }]
    }

    # Multiple subjects
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                    <marc:subfield code="a">sujet 1</marc:subfield>
                    <marc:subfield code="9">fre</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                    <marc:subfield code="a">sujet 2</marc:subfield>
                    <marc:subfield code="9">fre</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="653" ind1=" " ind2=" ">
                    <marc:subfield code="a">subject 1</marc:subfield>
                    <marc:subfield code="9">eng</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'subjects': [{
            'label': {
                'language': 'fre',
                'value': ['sujet 1', 'sujet 2']
            }
        }, {
            'label': {
                'language': 'eng',
                'value': ['subject 1']
            }
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
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'dissertation': {
            'degree': 'Dissertation degree'
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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {}


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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {}

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
    assert ArodesSchema().dump(xml) == {}

    # Not $g, with provision activity start date
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="269" ind1=" " ind2=" ">
                    <marc:subfield code="a">2019-01</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="773" ind1=" " ind2=" ">
                    <marc:subfield code="t">Host document</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'partOf': [{
            'document': {
                'title': 'Host document'
            },
            'numberingYear': '2019'
        }],
        'provisionActivity': [{
            'startDate': '2019-01-01',
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
                    <marc:subfield code="g">2015, vol. 37, no. 2, pp. 49-58</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'partOf': [{
            'document': {
                'title': 'Host document'
            },
            'numberingYear': '2015',
            'numberingVolume': '37',
            'numberingIssue': '2',
            'numberingPages': '49-58'
        }]
    }


def test_contribution():
    """Test contribution."""
    # No 700
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
    assert ArodesSchema().dump(xml) == {}

    # No 700$a
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="700" ind1=" " ind2=" ">
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {}

    # OK
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">John Doe</marc:subfield>
                    <marc:subfield code="u">RERO</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'contribution': [{
            'agent': {
                'preferred_name': 'John Doe',
                'type': 'bf:Person'
            },
            'role': ['ctb'],
            'affiliation': 'RERO'
        }]
    }

    # Multiple
    xml = '''
<record>
    <metadata>
        <marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <marc:record>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">John Doe</marc:subfield>
                    <marc:subfield code="u">RERO</marc:subfield>
                </marc:datafield>
                <marc:datafield tag="700" ind1=" " ind2=" ">
                    <marc:subfield code="a">Marc Landers</marc:subfield>
                    <marc:subfield code="u">HES-SO Valais</marc:subfield>
                </marc:datafield>
            </marc:record>
        </marc:collection>
    </metadata>
</record>
    '''
    assert ArodesSchema().dump(xml) == {
        'contribution': [{
            'agent': {
                'preferred_name': 'John Doe',
                'type': 'bf:Person'
            },
            'role': ['ctb'],
            'affiliation': 'RERO'
        }, {
            'agent': {
                'preferred_name': 'Marc Landers',
                'type': 'bf:Person'
            },
            'role': ['ctb'],
            'affiliation': 'HES-SO Valais'
        }]
    }
