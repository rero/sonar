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

"""DOJSON module tests."""

from __future__ import absolute_import, print_function

import pytest
from dojson.contrib.marc21.utils import create_record

from sonar.modules.documents.dojson.rerodoc.model import overdo


def test_marc21_to_type_and_organisation(app, bucket_location,
                                         without_oaiset_signals):
    """Test type and organisation."""

    # Type only
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('documentType') == 'coar:c_2f33'
    assert not data.get('organisation')

    # Type and organisation
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
            <subfield code="b">TEST</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('documentType') == 'coar:c_2f33'
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/test'
    }]

    # Type, subtype and organisation
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">POSTPRINT</subfield>
            <subfield code="b">TEST</subfield>
            <subfield code="f">ART_JOURNAL</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('documentType') == 'coar:c_6501'
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/test'
    }]

    # Organisation only
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">TEST</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('documentType')
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/test'
    }]

    # Specific conversion for unisi
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">UNISI</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('documentType')
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/usi'
    }]

    # Specific conversion for bpuge
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">BPUGE</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('documentType')
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/vge'
    }]
    assert len(data['subdivisions']) == 1

    # Specific conversion for mhnge
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">MHNGE</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('documentType')
    assert data.get('organisation') == [{
        '$ref':
        'https://sonar.ch/api/organisations/vge'
    }]
    assert len(data['subdivisions']) == 1


def test_marc21_to_title_245(app):
    """Test dojson marc21_to_title."""

    # One title with subtitle
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
            <subfield code="9">eng</subfield>
            <subfield code="b">Subtitle</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }],
        'subtitle': [{
            'value': 'Subtitle',
            'language': 'eng'
        }]
    }]

    # Multiple titles with subtitles
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
            <subfield code="9">eng</subfield>
            <subfield code="b">Subtitle</subfield>
        </datafield>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Titre principal</subfield>
            <subfield code="9">fre</subfield>
            <subfield code="b">Sous-titre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }],
        'subtitle': [{
            'value': 'Subtitle',
            'language': 'eng'
        }]
    }, {
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Titre principal',
            'language': 'fre'
        }],
        'subtitle': [{
            'value': 'Sous-titre',
            'language': 'fre'
        }]
    }]

    # One title without subtitle
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
            <subfield code="9">eng</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }]
    }]

    # No title
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="9">eng</subfield>
            <subfield code="b">Subtitle</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('title')

    # No language
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }]
    }]

    # Multiple title with one without title
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
            <subfield code="9">eng</subfield>
            <subfield code="b">Subtitle</subfield>
        </datafield>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="9">fre</subfield>
            <subfield code="b">Sous-titre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }],
        'subtitle': [{
            'value': 'Subtitle',
            'language': 'eng'
        }]
    }]


def test_marc21_to_title_246(app):
    """Test dojson marc21_to_title."""

    # One title 246 without 245
    marc21xml = """
    <record>
        <datafield tag="246" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
            <subfield code="9">eng</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }]
    }]

    # One title 246 without $a and without 245
    marc21xml = """
    <record>
        <datafield tag="246" ind1=" " ind2=" ">
            <subfield code="9">eng</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('title')

    # One title 246 without language and without 245
    marc21xml = """
    <record>
        <datafield tag="246" ind1=" " ind2=" ">
            <subfield code="a">Main title</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title',
            'language': 'eng'
        }]
    }]

    # One title 246 with one 245 title
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title 245</subfield>
            <subfield code="9">eng</subfield>
        </datafield>
        <datafield tag="246" ind1=" " ind2=" ">
            <subfield code="a">Main title 246</subfield>
            <subfield code="9">fre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title 245',
            'language': 'eng'
        }, {
            'value': 'Main title 246',
            'language': 'fre'
        }]
    }]

    # One title 246 with multiple 245 title
    marc21xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title 245 1</subfield>
            <subfield code="9">eng</subfield>
        </datafield>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Main title 245 2</subfield>
            <subfield code="9">eng</subfield>
        </datafield>
        <datafield tag="246" ind1=" " ind2=" ">
            <subfield code="a">Main title 246</subfield>
            <subfield code="9">fre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('title') == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title 245 1',
            'language': 'eng'
        }]
    }, {
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Main title 245 2',
            'language': 'eng'
        }, {
            'value': 'Main title 246',
            'language': 'fre'
        }]
    }]


def test_marc21_to_language(app):
    """Test language transformation."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="041" ind1=" " ind2=" ">
            <subfield code="a">fre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('language') == [{'type': 'bf:Language', 'value': 'fre'}]

    # Multiple $a
    marc21xml = """
    <record>
        <datafield tag="041" ind1=" " ind2=" ">
            <subfield code="a">eng</subfield>
            <subfield code="a">fre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'eng'
    }, {
        'type': 'bf:Language',
        'value': 'fre'
    }]

    # Multiple 041
    marc21xml = """
    <record>
        <datafield tag="041" ind1=" " ind2=" ">
            <subfield code="a">eng</subfield>
        </datafield>
        <datafield tag="041" ind1=" " ind2=" ">
            <subfield code="a">fre</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'eng'
    }, {
        'type': 'bf:Language',
        'value': 'fre'
    }]

    # Not $a
    marc21xml = """
    <record>
        <datafield tag="041" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('language')


def test_marc21_to_provision_activity_field_260(app):
    """Test provision activity with field 260."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">1798-1799</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
            <subfield code="e">Lausanne :</subfield>
            <subfield code="f">Henri Vincent</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        "type":
        "bf:Publication",
        "startDate":
        "1798",
        "endDate":
        "1799",
        "statement": [{
            "label": [{
                "value": "Lausanne"
            }],
            "type": "bf:Place"
        }, {
            "label": [{
                "value": "Bulletin officiel du Directoire"
            }],
            "type": "bf:Agent"
        }, {
            "label": [{
                "value": "1798-1799"
            }],
            "type": "Date"
        }]
    }, {
        "type":
        "bf:Manufacture",
        "statement": [{
            "label": [{
                "value": "Lausanne"
            }],
            "type": "bf:Place"
        }, {
            "label": [{
                "value": "Henri Vincent"
            }],
            "type": "bf:Agent"
        }]
    }]

    # No start date --> throw error
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')

    # No provision activity and wrong type --> throw error
    marc21xml = """
    <record></record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')

    # No provision activity and right types --> ok provision activity is not
    # mandatory
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">POSTPRINT</subfield>
            <subfield code="f">ART_JOURNAL</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')

    # Without end date
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">1798</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity')[0]['startDate'] == '1798'
    assert 'endDate' not in data.get('provisionActivity')[0]

    # Wrong start date
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">[1798?]</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert 'startDate' not in data.get('provisionActivity')[0]

    # Wrong end date
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">1798-</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert 'endDate' not in data.get('provisionActivity')[0]


def test_marc21_to_provision_activity_field_269(app):
    """Test provision activity with field 269."""
    # One field
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '1966',
        'type': 'bf:Publication'
    }]

    # One field with full date
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966-01-01</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '1966-01-01',
        'type': 'bf:Publication'
    }]

    # Date does not match "YYYY" OR "YYYY-MM-DD"
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966-1999</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')

    # Multiple fields
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">2005</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '2005',
        'type': 'bf:Publication'
    }]

    # No field $c
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="d">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')


def test_marc21_to_provision_activity_all(app):
    """Test provision activity with both 260 and 269 fields."""
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">1798-1799</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
            <subfield code="e">Lausanne :</subfield>
            <subfield code="f">Henri Vincent</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1700</subfield>
        </datafield>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 2</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        "type":
        "bf:Publication",
        "startDate":
        "1798",
        "endDate":
        "1799",
        "statement": [{
            "label": [{
                "value": "Lausanne"
            }],
            "type": "bf:Place"
        }, {
            "label": [{
                "value": "Bulletin officiel du Directoire"
            }],
            "type": "bf:Agent"
        }, {
            "label": [{
                "value": "1798-1799"
            }],
            "type": "Date"
        }]
    }, {
        "type":
        "bf:Manufacture",
        "statement": [{
            "label": [{
                "value": "Lausanne"
            }],
            "type": "bf:Place"
        }, {
            "label": [{
                "value": "Henri Vincent"
            }],
            "type": "bf:Agent"
        }]
    }]


def test_marc21_to_edition_statement(app):
    """Test edition statement dojson from field 250."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="a">Reproduction numérique</subfield>
            <subfield code="b">René Wetzel</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('editionStatement') == {
        'editionDesignation': {
            'value': 'Reproduction numérique'
        },
        'responsibility': {
            'value': 'René Wetzel'
        }
    }

    # Without field $a
    marc21xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="b">René Wetzel</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('editionStatement')

    # Without field $b
    marc21xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="a">Reproduction numérique</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('editionStatement')

    # Multiple --> keep only one value
    marc21xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="a">Reproduction numérique 1</subfield>
            <subfield code="b">John Doe</subfield>
        </datafield>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="a">Reproduction numérique 2</subfield>
            <subfield code="b">René Wetzel</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('editionStatement') == {
        'editionDesignation': {
            'value': 'Reproduction numérique 2'
        },
        'responsibility': {
            'value': 'René Wetzel'
        }
    }


# extent: 300$a (the first one if many)
# otherMaterialCharacteristics: 300$b (the first one if many)
# formats: 300 [$c repetitive]
def test_marc21_to_description(app):
    """Test dojson extent, otherMaterialCharacteristics, formats."""

    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">116 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">22 cm</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('extent') == '116 p.'
    assert data.get('otherMaterialCharacteristics') == 'ill.'
    assert data.get('formats') == ['22 cm']

    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">116 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">22 cm</subfield>
        <subfield code="c">12 x 15</subfield>
      </datafield>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">200 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">19 cm</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('extent') == '116 p.'
    assert data.get('otherMaterialCharacteristics') == 'ill.'
    assert data.get('formats') == ['22 cm', '12 x 15']

    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">116 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="x">22 cm</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('extent') == '116 p.'
    assert data.get('otherMaterialCharacteristics') == 'ill.'


# series.name: [490$a repetitive]
# series.number: [490$v repetitive]
def test_marc21_to_series(app):
    """Test dojson series."""

    marc21xml = """
    <record>
      <datafield tag="490" ind1=" " ind2=" ">
        <subfield code="a">Collection One</subfield>
        <subfield code="v">5</subfield>
      </datafield>
      <datafield tag="490" ind1=" " ind2=" ">
        <subfield code="a">Collection Two</subfield>
        <subfield code="v">123</subfield>
      </datafield>    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('series') == [{
        'name': 'Collection One',
        'number': '5'
    }, {
        'name': 'Collection Two',
        'number': '123'
    }]


def test_marc21_to_abstract(app):
    """Test dojson abstract."""

    # One abstract without language
    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">Abstract</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('abstracts') == [{'value': 'Abstract', 'language': 'eng'}]

    # One abstract with language
    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">Résumé</subfield>
        <subfield code="9">fre</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('abstracts') == [{'value': 'Résumé', 'language': 'fre'}]

    # Multiple abstracts
    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">Abstract</subfield>
        <subfield code="9">eng</subfield>
      </datafield>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">Résumé</subfield>
        <subfield code="9">fre</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('abstracts') == [{
        'value': 'Abstract',
        'language': 'eng'
    }, {
        'value': 'Résumé',
        'language': 'fre'
    }]

    # Without abstract
    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="9">eng</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('abstracts')

    # Special case with lang --> fr
    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">Résumé</subfield>
        <subfield code="9">fr</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('abstracts') == [{'value': 'Résumé', 'language': 'fre'}]


# notes: [500$a repetitive]
def test_marc21_to_notes(app):
    """Test dojson notes."""

    marc21xml = """
    <record>
      <datafield tag="500" ind1=" " ind2=" ">
        <subfield code="a">note 1</subfield>
      </datafield>
      <datafield tag="500" ind1=" " ind2=" ">
        <subfield code="a">note 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('notes') == ['note 1', 'note 2']


# subjects: 6xx [duplicates could exist between several vocabularies,
# if possible deduplicate]
def test_marc21_to_subjects(app):
    """Test dojson subjects."""

    marc21xml = """
    <record>
      <datafield tag="695" ind1=" " ind2=" ">
        <subfield code="9">eng</subfield>
        <subfield code="a">subject 1 ; subject 2</subfield>
      </datafield>
      <datafield tag="695" ind1=" " ind2=" ">
        <subfield code="9">fre</subfield>
        <subfield code="a">sujet 1 ; sujet 2</subfield>
      </datafield>
      <datafield tag="600" ind1=" " ind2=" ">
        <subfield code="2">rero</subfield>
        <subfield code="a">subject 600 1 ; subject 600 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('subjects') == [{
        'label': {
            'language': 'eng',
            'value': ['subject 1', 'subject 2']
        }
    }, {
        'label': {
            'language': 'fre',
            'value': ['sujet 1', 'sujet 2']
        }
    }, {
        'label': {
            'value': ['subject 600 1', 'subject 600 2']
        },
        'source': 'rero'
    }]

    # 600 without $a
    marc21xml = """
    <record>
      <datafield tag="600" ind1=" " ind2=" ">
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('subjects')

    # 600 without source
    marc21xml = """
    <record>
      <datafield tag="600" ind1=" " ind2=" ">
        <subfield code="a">subject 600 1 ; subject 600 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('subjects')

    # 695 without language
    marc21xml = """
    <record>
      <datafield tag="695" ind1=" " ind2=" ">
        <subfield code="a">subject 1 ; subject 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('subjects')


def test_marc21_to_identified_by_from_001(app):
    """Test identifiedBy from 001."""

    marc21xml = """
    <record>
      <controlfield tag="001">327171</controlfield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'RERO DOC',
        'value': '327171'
    }]

    marc21xml = "<record></record>"
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_020(app):
    """Test identifiedBy from 020."""

    marc21xml = """
    <record>
        <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="a">9783796539138</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Isbn',
        'value': '9783796539138'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="b">9783796539138</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_024(app):
    """Test identifiedBy from 024."""

    marc21xml = """
    <record>
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="a">urn:nbn:ch:rero-002-118667</subfield>
            <subfield code="2">urn</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Urn',
        'value': 'urn:nbn:ch:rero-002-118667'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="2">urn</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')

    # Without code $2
    marc21xml = """
    <record>
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="a">urn:nbn:ch:rero-002-118667</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')

    # $2 is a falsy value
    marc21xml = """
    <record>
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="a">urn:nbn:ch:rero-002-118667</subfield>
            <subfield code="2">falsy_value</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')

    # Without ind1 == 7
    marc21xml = """
    <record>
        <datafield tag="024" ind1=" " ind2=" ">
            <subfield code="a">urn:nbn:ch:rero-002-118667</subfield>
            <subfield code="2">falsy_value</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_027(app):
    """Test identifiedBy from 027."""

    marc21xml = """
    <record>
        <datafield tag="027" ind1=" " ind2=" ">
            <subfield code="a">9789027223951</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Strn',
        'value': '9789027223951'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="027" ind1=" " ind2=" ">
            <subfield code="b">9789027223951</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_035(app):
    """Test identifiedBy from 035."""

    marc21xml = """
    <record>
        <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="a">R008966083</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'RERO',
        'value': 'R008966083'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="b">R008966083</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_037(app):
    """Test identifiedBy from 037."""

    marc21xml = """
    <record>
        <datafield tag="037" ind1=" " ind2=" ">
            <subfield code="a">
                swissbib.ch:(NATIONALLICENCE)springer-10.1007/s00209-014-1344-0
            </subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type':
        'bf:Local',
        'source':
        'Swissbib',
        'value':
        '(NATIONALLICENCE)springer-10.1007/s00209-014-1344-0'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="037" ind1=" " ind2=" ">
            <subfield code="b">
                swissbib.ch:(NATIONALLICENCE)springer-10.1007/s00209-014-1344-0
            </subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_088(app):
    """Test identifiedBy from 088."""

    marc21xml = """
    <record>
        <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a">25</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:ReportNumber',
        'value': '25'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="b">25</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_091(app):
    """Test identifiedBy from 091."""

    marc21xml = """
    <record>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="a">24638240</subfield>
            <subfield code="b">pmid</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'value': '24638240',
        'source': 'PMID'
    }]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="b">pmid</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')

    # Without code $b
    marc21xml = """
    <record>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="a">24638240</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')

    # Invalid code $b
    marc21xml = """
    <record>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="a">24638240</subfield>
            <subfield code="b">fake</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_full(app):
    """Test full identified by."""
    marc21xml = """
    <record>
        <controlfield tag="001">327171</controlfield>
        <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="a">9783796539138</subfield>
        </datafield>
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="a">urn:nbn:ch:rero-002-118667</subfield>
            <subfield code="2">urn</subfield>
        </datafield>
        <datafield tag="027" ind1=" " ind2=" ">
            <subfield code="a">9789027223951</subfield>
        </datafield>
        <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="a">R008966083</subfield>
        </datafield>
        <datafield tag="037" ind1=" " ind2=" ">
            <subfield code="a">
                swissbib.ch:(NATIONALLICENCE)springer-10.1007/s00209-014-1344-0
            </subfield>
        </datafield>
        <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a">25</subfield>
        </datafield>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="a">24638240</subfield>
            <subfield code="b">pmid</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'RERO DOC',
        'value': '327171'
    }, {
        'type': 'bf:Isbn',
        'value': '9783796539138'
    }, {
        'type': 'bf:Urn',
        'value': 'urn:nbn:ch:rero-002-118667'
    }, {
        'type': 'bf:Strn',
        'value': '9789027223951'
    }, {
        'type': 'bf:Local',
        'source': 'RERO',
        'value': 'R008966083'
    }, {
        'type':
        'bf:Local',
        'source':
        'Swissbib',
        'value':
        '(NATIONALLICENCE)springer-10.1007/s00209-014-1344-0'
    }, {
        'type': 'bf:ReportNumber',
        'value': '25'
    }, {
        'type': 'bf:Local',
        'value': '24638240',
        'source': 'PMID'
    }]


def test_marc21_to_files(app):
    """Test getting files from field 856."""
    # Only one file
    marc21xml = """
    <record>
    <datafield tag="856" ind1="4" ind2=" ">
        <subfield code="f">file.pdf</subfield>
        <subfield code="q">application/pdf</subfield>
        <subfield code="s">1467377</subfield>
        <subfield code="u">
            http://some.url/file.pdf
        </subfield>
        <subfield code="y">order:1</subfield>
        <subfield code="z">Dépliant de l'exposition</subfield>
    </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert len(data.get('files')) == 1
    assert data.get('files')[0]['key'] == 'file.pdf'
    assert data.get('files')[0]['url'] == 'http://some.url/file.pdf'
    assert data.get('files')[0]['label'] == 'Dépliant de l\'exposition'
    assert data.get('files')[0]['order'] == 1

    # Not key
    marc21xml = """
    <record>
    <datafield tag="856" ind1="4" ind2=" ">
        <subfield code="q">application/pdf</subfield>
        <subfield code="s">1467377</subfield>
        <subfield code="u">
            http://some.url/file.pdf
        </subfield>
        <subfield code="y">order:1</subfield>
        <subfield code="z">Dépliant de l'exposition</subfield>
    </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('files')

    # Not URL
    marc21xml = """
    <record>
    <datafield tag="856" ind1="4" ind2=" ">
        <subfield code="f">file.pdf</subfield>
        <subfield code="q">application/pdf</subfield>
        <subfield code="s">1467377</subfield>
        <subfield code="y">order:1</subfield>
        <subfield code="z">Dépliant de l'exposition</subfield>
    </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('files')

    # Wrong mime type
    marc21xml = """
    <record>
    <controlfield tag="001">327171</controlfield>
    <datafield tag="856" ind1="4" ind2=" ">
        <subfield code="f">file.pdf</subfield>
        <subfield code="q">pdt/download</subfield>
        <subfield code="s">1467377</subfield>
        <subfield code="u">
            http://some.url/file.pdf
        </subfield>
        <subfield code="y">order:1</subfield>
        <subfield code="z">Dépliant de l'exposition</subfield>
    </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('files')


def test_marc21_to_other_edition(app):
    """Test other edition extraction."""
    # One other edition
    marc21xml = """
    <record>
        <datafield tag="775" ind1=" " ind2=" ">
            <subfield code="o">http://domain.com/url</subfield>
            <subfield code="g">version publiée</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('otherEdition') == [{
        'document': {
            'electronicLocator': 'http://domain.com/url'
        },
        'publicNote': 'version publiée'
    }]

    # Multiple other editions
    marc21xml = """
    <record>
        <datafield tag="775" ind1=" " ind2=" ">
            <subfield code="o">http://domain.com/url</subfield>
            <subfield code="g">version publiée</subfield>
        </datafield>
        <datafield tag="775" ind1=" " ind2=" ">
            <subfield code="o">http://domain.com/url-2</subfield>
            <subfield code="g">version publiée</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('otherEdition') == [{
        'document': {
            'electronicLocator': 'http://domain.com/url'
        },
        'publicNote': 'version publiée'
    }, {
        'document': {
            'electronicLocator': 'http://domain.com/url-2'
        },
        'publicNote': 'version publiée'
    }]

    # No electronic location
    marc21xml = """
    <record>
        <datafield tag="775" ind1=" " ind2=" ">
            <subfield code="g">version publiée</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('otherEdition')

    # No public note
    marc21xml = """
    <record>
        <datafield tag="775" ind1=" " ind2=" ">
            <subfield code="o">http://domain.com/url</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('otherEdition')


def test_marc21_to_specific_collection(app, bucket_location,
                                       without_oaiset_signals):
    """Test extracting collection from file 982."""
    # No code a
    marc21xml = """
    <record>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="b">Treize étoiles</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('collections')

    # Not field 982
    marc21xml = """
    <record>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('collections')

    # No organisation
    marc21xml = """
    <record>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Treize étoiles</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('collections')

    # OK
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">test-org</subfield>
        </datafield>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Treize étoiles</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data['collections']

    # Multiple collections
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">test-org</subfield>
        </datafield>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Collection 1</subfield>
        </datafield>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Collection 2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert len(data['collections']) == 2


def test_marc21_to_classification_from_field_080(app):
    """Test classification from field 080."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="080" ind1=" " ind2=" ">
            <subfield code="a">82</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('classification') == [{
        "type": "bf:ClassificationUdc",
        "classificationPortion": "82"
    }]

    # Not $a record
    marc21xml = """
    <record>
        <datafield tag="080" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('classification')


def test_marc21_to_classification_from_field_084(app):
    """Test classification from field 084."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="084" ind1=" " ind2=" ">
            <subfield code="a">610</subfield>
            <subfield code="2">ddc</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('classification') == [{
        "type": "bf:ClassificationDdc",
        "classificationPortion": "610"
    }]

    # Not $a record
    marc21xml = """
    <record>
        <datafield tag="084" ind1=" " ind2=" ">
            <subfield code="2">ddc</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('classification')

    # Not $2 record
    marc21xml = """
    <record>
        <datafield tag="084" ind1=" " ind2=" ">
            <subfield code="a">610</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('classification')


def test_marc21_to_classification_from_all(app):
    """Test classification from all field."""
    marc21xml = """
    <record>
        <datafield tag="080" ind1=" " ind2=" ">
            <subfield code="a">82</subfield>
        </datafield>
        <datafield tag="084" ind1=" " ind2=" ">
            <subfield code="a">610</subfield>
            <subfield code="2">ddc</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('classification') == [{
        "type": "bf:ClassificationUdc",
        "classificationPortion": "82"
    }, {
        "type": "bf:ClassificationDdc",
        "classificationPortion": "610"
    }]


def test_marc21_to_content_note(app):
    """Test extracting content notes from field 505."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="505" ind1=" " ind2=" ">
            <subfield code="a">La comtesse de Mortane</subfield>
        </datafield>
        <datafield tag="505" ind1=" " ind2=" ">
            <subfield code="a">Voyage de campagne</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contentNote') == [
        'La comtesse de Mortane', 'Voyage de campagne'
    ]

    # No field $a
    marc21xml = """
    <record>
        <datafield tag="505" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('contentNote')


def test_marc21_to_dissertation_field_502(app):
    """Test extracting dissertation degree from field 502."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse de doctorat</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {'degree': 'Thèse de doctorat'}

    # thesis note decomposition
    marc21xml = """
    <datafield tag="502" ind1=" " ind2=" ">
        <subfield code="a">Thèse de doctorat : Université de Fribourg, 2010 ; Nr. 1671</subfield>
    </datafield>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {
        'degree': 'Thèse de doctorat',
        'grantingInstitution': 'Université de Fribourg',
        'date': '2010'
    }
    
    # Multiple --> keep always last value
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse de doctorat</subfield>
        </datafield>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Last degree</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {'degree': 'Last degree'}

    # Without $a
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" "></datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('dissertation')


def test_marc21_to_dissertation_field_508(app):
    """Test extracting dissertation notes from field 508."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="508" ind1=" " ind2=" ">
            <subfield code="a">Magna cum laude</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {'jury_note': 'Magna cum laude'}

    # Multiple
    marc21xml = """
    <record>
        <datafield tag="508" ind1=" " ind2=" ">
            <subfield code="a">Note 1</subfield>
        </datafield>
        <datafield tag="508" ind1=" " ind2=" ">
            <subfield code="a">Note 2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {'jury_note': 'Note 2'}

    # Without $a
    marc21xml = """
    <record>
        <datafield tag="508" ind1=" " ind2=" "></datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('dissertation')


def test_marc21_to_dissertation_all(app):
    """Test extracting dissertation notes and degree."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse de doctorat</subfield>
        </datafield>
        <datafield tag="508" ind1=" " ind2=" ">
            <subfield code="a">Magna cum laude</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('dissertation') == {
        'degree': 'Thèse de doctorat',
        'jury_note': 'Magna cum laude'
    }


def test_marc21_to_usage_and_access_policy(app):
    """Test extracting usage and access policy."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="540" ind1=" " ind2=" ">
            <subfield code="a">Springer-Verlag Berlin</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('usageAndAccessPolicy') == {
        'label': 'Springer-Verlag Berlin',
        'license': 'License undefined'
    }

    # Multiple
    marc21xml = """
    <record>
        <datafield tag="540" ind1=" " ind2=" ">
            <subfield code="a">Usage 1</subfield>
        </datafield>
        <datafield tag="540" ind1=" " ind2=" ">
            <subfield code="a">Usage 2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('usageAndAccessPolicy') == {
        'label': 'Usage 2',
        'license': 'License undefined'
    }

    # Without $a
    marc21xml = """
    <record>
        <datafield tag="540" ind1=" " ind2=" "></datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('usageAndAccessPolicy') == {
        'license': 'License undefined'
    }

    # Without 540
    marc21xml = """
    <record></record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('usageAndAccessPolicy') == {
        'license': 'License undefined'
    }


def test_marc21_to_contribution_field_100(app):
    """Test extracting contribution from field 100."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="d">1980-2010</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980',
            'date_of_death': '2010'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland'
    }]

    # Not $a
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="d">1980-2010</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('contribution')

    # Date does not match
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="d">zzzz</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    with pytest.raises(Exception) as exception:
        data = overdo.do(marc21json)
    assert str(exception.value) == 'Date "zzzz" is not recognized'

    # Only birth date
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="d">1980-</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland'
    }]

    # Only birth date, variant 2
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="d">1980</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland'
    }]

    # Only birth date, variant 3
    marc21xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Romagnani, Andrea</subfield>
            <subfield code="d">1980-04-04</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980-04-04'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland'
    }]


def test_marc21_to_contribution_field_700(app):
    """Test extracting contribution from field 700."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
            <subfield code="d">1980-2010</subfield>
            <subfield code="e">Dir.</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Piguet, Etienne',
            'date_of_birth': '1980',
            'date_of_death': '2010'
        },
        'role': ['dgs'],
        'affiliation':
        'University of Bern, Switzerland'
    }]

    # Not $a
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="d">1980-2010</subfield>
            <subfield code="e">Dir.</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('contribution')

    # Only birth date
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
            <subfield code="d">1980-</subfield>
            <subfield code="e">Dir.</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Piguet, Etienne',
            'date_of_birth': '1980'
        },
        'role': ['dgs'],
        'affiliation':
        'University of Bern, Switzerland'
    }]

    # Role from field 980, but not existing
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
            <subfield code="d">1980-</subfield>
            <subfield code="u">University of Bern, Switzerland</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    with pytest.raises(Exception) as exception:
        data = overdo.do(marc21json)
    assert str(exception.value).startswith('No role found for contributor')

    # Role from field 980, but 980 is not mapped
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">NOT EXISTING</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    with pytest.raises(Exception) as exception:
        data = overdo.do(marc21json)
    assert str(exception.value).startswith('No role found for contributor')

    # Role from field 980, but $a is not existing
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    with pytest.raises(Exception) as exception:
        data = overdo.do(marc21json)
    assert str(exception.value).startswith('No role found for contributor')

    # Role from field 980, found 'cre'
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">POSTPRINT</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution')[0]['role'] == ['cre']

    # Role from field 980, found 'ctb'
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution')[0]['role'] == ['ctb']

    # Role 'prt' found
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
            <subfield code="e">Libr./Impr.</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution')[0]['role'] == ['prt']

    # Role for joint author
    marc21xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Piguet, Etienne</subfield>
            <subfield code="e">joint author</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution')[0]['role'] == ['cre']


def test_marc21_to_contribution_field_710(app):
    """Test extracting contribution from field 710."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="710" ind1=" " ind2=" ">
            <subfield code="a">Musée d'art et d'histoire</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Organization',
            'preferred_name': 'Musée d\'art et d\'histoire'
        },
        'role': ['ctb'],
    }]

    # No $a
    marc21xml = """
    <record>
        <datafield tag="710" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('contribution')


def test_marc21_to_contribution_field_711(app):
    """Test extracting contribution from field 711."""
    # OK
    marc21xml = """
    <record>
        <datafield tag="711" ind1=" " ind2=" ">
            <subfield code="a">Theologisches Forum Christentum</subfield>
            <subfield code="c">Stuttgart-Hohenheim</subfield>
            <subfield code="d">2004</subfield>
            <subfield code="n">2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Meeting',
            'preferred_name': 'Theologisches Forum Christentum',
            'place': 'Stuttgart-Hohenheim',
            'date': '2004',
            'number': '2'
        },
        'role': ['cre'],
    }]

    # Not $a
    marc21xml = """
    <record>
        <datafield tag="711" ind1=" " ind2=" ">
            <subfield code="c">Stuttgart-Hohenheim</subfield>
            <subfield code="d">2004</subfield>
            <subfield code="n">2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('contribution')


def test_marc21_to_part_of(app):
    """Test extracting is part of from field 773."""
    # With sub type of ART INBOOK
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="c">Belser, Eva Maria</subfield>
            <subfield code="t">Mehr oder weniger Staat?</subfield>
            <subfield code="g">2015///</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('partOf') == [{
        'numberingYear': '2015',
        'document': {
            'title': 'Mehr oder weniger Staat?',
            'contribution': ['Belser, Eva Maria'],
            'publication': {
                'statement': 'Stämpfli Verlag, Bern',
                'startDate': '2015'
            }
        }
    }]
    assert data.get('provisionActivity') == [{
        'startDate': '2015',
        'type': 'bf:Publication'
    }]

    # With sub type is not ART INBOOK
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="t">Optics Express</subfield>
            <subfield code="g">2020/28/6/8200-8210</subfield>
            <subfield code="d">Optical Society of America</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_JOURNAL</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('partOf') == [{
        'numberingYear': '2020',
        'numberingVolume': '28',
        'numberingIssue': '6',
        'numberingPages': '8200-8210',
        'document': {
            'title': 'Optics Express',
            'publication': {
                'statement': 'Optical Society of America'
            }
        }
    }]
    assert data.get('provisionActivity') == [{
        'startDate': '2020',
        'type': 'bf:Publication'
    }]

    # Without $g
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="c">Belser, Eva Maria</subfield>
            <subfield code="t">Mehr oder weniger Staat?</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('partOf')
    assert not data.get('provisionActivity')

    # Without empty numbering year
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="g">///-</subfield>
            <subfield code="c">Belser, Eva Maria</subfield>
            <subfield code="t">Mehr oder weniger Staat?</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('partOf')
    assert not data.get('provisionActivity')

    # Without numbering year
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="c">Belser, Eva Maria</subfield>
            <subfield code="g"></subfield>
            <subfield code="t">Mehr oder weniger Staat?</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('partOf')
    assert not data.get('provisionActivity')

    # Without title
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="c">Belser, Eva Maria</subfield>
            <subfield code="g">2015///</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('partOf') == [{
        'numberingYear': '2015',
        'document': {
            'contribution': ['Belser, Eva Maria'],
            'publication': {
                'startDate': '2015',
                'statement': 'Stämpfli Verlag, Bern'
            }
        }
    }]
    assert data.get('provisionActivity') == [{
        'startDate': '2015',
        'type': 'bf:Publication'
    }]

    # Without $c
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="t">Mehr oder weniger Staat?</subfield>
            <subfield code="g">2015///</subfield>
            <subfield code="d">Stämpfli Verlag, Bern</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_INBOOK</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('partOf') == [{
        'numberingYear': '2015',
        'document': {
            'title': 'Mehr oder weniger Staat?',
            'publication': {
                'statement': 'Stämpfli Verlag, Bern',
                'startDate': '2015'
            }
        }
    }]
    assert data.get('provisionActivity') == [{
        'startDate': '2015',
        'type': 'bf:Publication'
    }]

    # Without document
    marc21xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="g">2015///</subfield>
        </datafield>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="f">ART_JOURNAL</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('partOf') == [{'numberingYear': '2015'}]
    assert data.get('provisionActivity') == [{
        'startDate': '2015',
        'type': 'bf:Publication'
    }]


def test_start_date_priorities(app):
    """Test start date priorities for provision activity."""
    # Four potential start dates.
    marc21xml = """
    <record>
        <datafield tag="260" ind1=" " ind2=" ">
            <subfield code="a">Lausanne</subfield>
            <subfield code="c">1798-1799</subfield>
            <subfield code="b">Bulletin officiel du Directoire,</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="g">2015///</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data['provisionActivity'][0]['startDate'] == '1798'

    # Start dates from 269$c must be taken.
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="g">2015///</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data['provisionActivity'][0]['startDate'] == '1966'

    # Start dates from 773$g must be taken.
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="g">2015///</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data['provisionActivity'][0]['startDate'] == '2015'

    # Only 502$9
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data['provisionActivity'][0]['startDate'] == '2020'


def test_marc21_to_provision_activity_field_502(app):
    """Test provision activity with field 502."""
    # One field
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '2020',
        'type': 'bf:Publication'
    }]

    # One field with full date
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2020-09-09</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '2020-09-09',
        'type': 'bf:Publication'
    }]

    # Date does not match "YYYY" OR "YYYY-MM-DD"
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2010-2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')

    # Multiple fields
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 1</subfield>
            <subfield code="9">2010</subfield>
        </datafield>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 2</subfield>
            <subfield code="9">2020</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '2020',
        'type': 'bf:Publication'
    }]

    # No field $9
    marc21xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Thèse 2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = overdo.do(marc21json)
    assert not data.get('provisionActivity')
