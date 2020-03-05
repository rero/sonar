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

"""DOJSON module tests."""

from __future__ import absolute_import, print_function

import os

import mock
import pytest
from dojson.contrib.marc21.utils import create_record
from utils import mock_response

from sonar.modules.documents.dojson.contrib.marc21tojson import marc21tojson
from sonar.modules.documents.dojson.contrib.marc21tojson.model import \
    get_person_link
from sonar.modules.documents.dojson.utils import not_repetitive
from sonar.modules.documents.views import create_publication_statement


def test_not_repetetive(capsys):
    """Test the function not_repetetive."""
    data_dict = {'sub': ('first', 'second')}
    data = not_repetitive('pid1', 'key', data_dict, 'sub')
    assert data == 'first'
    out, err = capsys.readouterr()
    assert err == 'WARNING NOT REPETITIVE:\tpid1\tkey\tsub\t{data}\t\n'.format(
        data=str(data_dict))
    data = {'sub': 'only'}
    data = not_repetitive('pid1', 'key', data, 'sub', '')
    assert data == 'only'
    out, err = capsys.readouterr()
    assert err == ""


def test_marc21_to_type_and_institution(app):
    """Test type and institution."""

    # Type and institution
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
            <subfield code="b">BAAGE</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('type') == 'book'
    assert data.get('institution') == {
        '$ref': 'https://sonar.ch/api/institutions/baage'
    }

    # Type only
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('type') == 'book'
    assert not data.get('institution')

    # Institution only
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="b">BAAGE</subfield>
        </datafield>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data.get('type')
    assert data.get('institution') == {
        '$ref': 'https://sonar.ch/api/institutions/baage'
    }


def test_marc21_to_title_245():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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


def test_marc21_to_title_246():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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


# languages: 008 and 041 [$a, repetitive]
def test_marc21_to_language():
    """Test dojson marc21languages."""

    marc21xml = """
    <record>
      <controlfield tag="008">{field_008}</controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">ara</subfield>
        <subfield code="a">eng</subfield>
      </datafield>
    </record>
    """.format(field_008='881005s1984    xxu|||||| ||||00|| |ara d')
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)

    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'ara'
    }, {
        'type': 'bf:Language',
        'value': 'eng'
    }]

    marc21xml = """
    <record>
      <controlfield tag="008">{field_008}</controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">eng</subfield>
      </datafield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">fre</subfield>
      </datafield>
    </record>
    """.format(field_008='881005s1984    xxu|||||| ||||00|| |ara d')
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'ara'
    }, {
        'type': 'bf:Language',
        'value': 'eng'
    }, {
        'type': 'bf:Language',
        'value': 'fre'
    }]

    marc21xml = """
    <record>
      <datafield tag="041" ind1=" " ind2=" ">
      <subfield code="a">eng</subfield>
    </datafield>
    <controlfield tag="008">{field_008}</controlfield>
    </record>
    """.format(field_008='881005s1984    xxu|||||| ||||00|| |ara d')
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)

    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'ara'
    }, {
        'type': 'bf:Language',
        'value': 'eng'
    }]

    marc21xml = """
    <record>
      <controlfield tag="008">{field_008}</controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">eng</subfield>
        <subfield code="a">rus</subfield>
      </datafield>
    </record>
    """.format(field_008='881005s1984    xxu|||||| ||||00|| |ara d')
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('language') == [{
        'type': 'bf:Language',
        'value': 'ara'
    }, {
        'type': 'bf:Language',
        'value': 'eng'
    }, {
        'type': 'bf:Language',
        'value': 'rus'
    }]

    marc21xml = """
    <record>
      <controlfield tag="008">{field_008}</controlfield>
    </record>
    """.format(field_008='881005s1984    xxu|||||| ||||00|| |ara d')
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data.get('language')


# authors: loop:
# authors.name: 100$a [+ 100$b if it exists] or
#   [700$a (+$b if it exists) repetitive] or
#   [ 710$a repetitive (+$b if it exists, repetitive)]
# authors.date: 100 $d or 700 $d (facultatif)
# authors.qualifier: 100 $c or 700 $c (facultatif)
# authors.type: if 100 or 700 then person, if 710 then organisation
@mock.patch('requests.get')
def test_marc21_to_authors(mock_get):
    """Test dojson marc21_to_authors."""

    marc21xml = """
    <record>
      <datafield tag="100" ind1=" " ind2=" ">
        <subfield code="a">Jean-Paul</subfield>
        <subfield code="b">II</subfield>
        <subfield code="c">Pape</subfield>
        <subfield code="d">1954-</subfield>
      </datafield>
      <datafield tag="700" ind1=" " ind2=" ">
        <subfield code="a">Dumont, Jean</subfield>
        <subfield code="c">Historien</subfield>
        <subfield code="d">1921-2014</subfield>
      </datafield>
      <datafield tag="710" ind1=" " ind2=" ">
        <subfield code="a">RERO</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    authors = data.get('authors')
    assert authors == [{
        'name': 'Jean-Paul II',
        'type': 'person',
        'date': '1954-',
        'qualifier': 'Pape'
    }, {
        'name': 'Dumont, Jean',
        'type': 'person',
        'date': '1921-2014',
        'qualifier': 'Historien'
    }, {
        'name': 'RERO',
        'type': 'organisation'
    }]
    marc21xml = """
    <record>
      <datafield tag="100" ind1=" " ind2=" ">
        <subfield code="a">Jean-Paul</subfield>
        <subfield code="b">II</subfield>
        <subfield code="c">Pape</subfield>
        <subfield code="d">1954-</subfield>
      </datafield>
      <datafield tag="700" ind1=" " ind2="2">
        <subfield code="a">Dumont, Jean</subfield>
        <subfield code="c">Historien</subfield>
        <subfield code="d">1921-2014</subfield>
      </datafield>
      <datafield tag="710" ind1=" " ind2=" ">
        <subfield code="a">RERO</subfield>
        <subfield code="c">Martigny</subfield>
        <subfield code="d">1971</subfield>
      </datafield>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    authors = data.get('authors')
    assert authors == [{
        'name': 'Jean-Paul II',
        'type': 'person',
        'date': '1954-',
        'qualifier': 'Pape'
    }, {
        'name': 'RERO',
        'type': 'organisation'
    }]

    marc21xml = """
    <record>
      <datafield tag="100" ind1=" " ind2=" ">
        <subfield code="0">(RERO)XXXXXXXX</subfield>
      </datafield>
    </record>
    """
    mock_get.return_value = mock_response(
        json_data={
            'hits': {
                'hits': [{
                    'links': {
                        'self': 'https://mef.rero.ch/api/rero/XXXXXXXX'
                    }
                }]
            }
        })
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    authors = data.get('authors')
    assert authors == [{
        '$ref': 'https://mef.rero.ch/api/rero/XXXXXXXX',
        'type': 'person'
    }]


# Copyright Date: [264 _4 $c non repetitive]
def test_marc21copyrightdate():
    """Test dojson Copyright Date."""

    marc21xml = """
    <record>
      <datafield tag="264" ind1=" " ind2="4">
        <subfield code="c">© 1971</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('copyrightDate') == ['© 1971']

    marc21xml = """
    <record>
      <datafield tag="264" ind1=" " ind2="4">
        <subfield code="c">© 1971 [extra 1973]</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('copyrightDate') == ['© 1971 [extra 1973]']


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
    data = marc21tojson.do(marc21json)
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
            "type":
            "bf:Agent"
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
    data = marc21tojson.do(marc21json)
    assert not data.get('provisionActivity')

    # No provision activity and wrong type --> throw error
    marc21xml = """
    <record></record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity')[0]['startDate'] == '1798'
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
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '1966',
        'type': 'bf:Publication'
    }]

    # One field with start and end date
    marc21xml = """
    <record>
        <datafield tag="269" ind1=" " ind2=" ">
            <subfield code="c">1966-1999</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'startDate': '1966',
        'type': 'bf:Publication'
    }]

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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('provisionActivity')


def test_marc21_to_provision_activity_all():
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
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
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
    }, {
        "type":
        "bf:Publication",
        "startDate":
        "1700",
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
            "type":
            "bf:Agent"
        }, {
            "label": [{
                "value": "1798-1799"
            }],
            "type": "Date"
        }]
    }]


def test_marc21_to_edition_statement_one_field_250():
    """Test dojson edition statement.
    - 1 edition designation and 1 responsibility from field 250
    - extract data from the linked 880 from field 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |chi d</controlfield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="6">880-02</subfield>
        <subfield code="a">Di 3 ban /</subfield>
        <subfield code="b">Zeng Lingliang zhu bian</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2=" ">
        <subfield code="6">250-02/$1</subfield>
        <subfield code="a">第3版 /</subfield>
        <subfield code="b">曾令良主编</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('editionStatement') == [{
        'editionDesignation': [{
            'value': 'Di 3 ban'
        }, {
            'value': '第3版',
            'language': 'chi-hani'
        }],
        'responsibility': [{
            'value': 'Zeng Lingliang zhu bian'
        }, {
            'value': '曾令良主编',
            'language': 'chi-hani'
        }]
    }]


def test_marc21_to_edition_statement_two_fields_250():
    """Test dojson edition statement.
    - 2 edition designation and 2 responsibility from fields 250
    - extract data from the linked 880 from 1 field 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |chi d</controlfield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="6">880-02</subfield>
        <subfield code="a">Di 3 ban /</subfield>
        <subfield code="b">Zeng Lingliang zhu bian</subfield>
      </datafield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="a">Edition /</subfield>
        <subfield code="b">Responsibility</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2=" ">
        <subfield code="6">250-02/$1</subfield>
        <subfield code="a">第3版 /</subfield>
        <subfield code="b">曾令良主编</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('editionStatement') == [{
        'editionDesignation': [{
            'value': 'Di 3 ban'
        }, {
            'value': '第3版',
            'language': 'chi-hani'
        }],
        'responsibility': [{
            'value': 'Zeng Lingliang zhu bian'
        }, {
            'value': '曾令良主编',
            'language': 'chi-hani'
        }]
    }, {
        'editionDesignation': [{
            'value': 'Edition'
        }],
        'responsibility': [{
            'value': 'Responsibility'
        }]
    }]


def test_marc21_to_edition_statement_with_two_subfield_a():
    """Test dojson edition statement.
    - 1 field 250 with 2 subfield_a
    - extract data from the linked 880 from 1 field 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |chi d</controlfield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="6">880-02</subfield>
        <subfield code="a">Di 3 ban /</subfield>
        <subfield code="a">Di 4 ban /</subfield>
        <subfield code="b">Zeng Lingliang zhu bian</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2=" ">
        <subfield code="6">250-02/$1</subfield>
        <subfield code="a">第3版 /</subfield>
        <subfield code="a">第4版 /</subfield>
        <subfield code="b">曾令良主编</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)

    assert data.get('editionStatement') == [{
        'editionDesignation': [{
            'value': 'Di 3 ban'
        }, {
            'value': '第3版',
            'language': 'chi-hani'
        }],
        'responsibility': [{
            'value': 'Zeng Lingliang zhu bian'
        }, {
            'value': '曾令良主编',
            'language': 'chi-hani'
        }]
    }]


def test_marc21_to_edition_statement_with_one_bad_field_250():
    """Test dojson edition statement.
    - 3 fields 250, and one of them as bad subdields $x, $y
      and one as only $b
    - extract data from the linked 880 from 1 field 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |chi d</controlfield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="6">880-02</subfield>
        <subfield code="a">Di 3 ban /</subfield>
        <subfield code="b">Zeng Lingliang zhu bian</subfield>
      </datafield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="x">Edition /</subfield>
        <subfield code="y">Responsibility</subfield>
      </datafield>
      <datafield  tag="250" ind1=" " ind2=" ">
        <subfield code="a">Edition</subfield>
        <subfield code="y">Responsibility</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2=" ">
        <subfield code="6">250-02/$1</subfield>
        <subfield code="a">第3版 /</subfield>
        <subfield code="b">曾令良主编</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('editionStatement') == [{
        'editionDesignation': [{
            'value': 'Di 3 ban'
        }, {
            'value': '第3版',
            'language': 'chi-hani'
        }],
        'responsibility': [{
            'value': 'Zeng Lingliang zhu bian'
        }, {
            'value': '曾令良主编',
            'language': 'chi-hani'
        }]
    }, {
        'editionDesignation': [{
            'value': 'Edition'
        }]
    }]


# extent: 300$a (the first one if many)
# otherMaterialCharacteristics: 300$b (the first one if many)
# formats: 300 [$c repetitive]
def test_marc21_to_description():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert data.get('extent') == '116 p.'
    assert data.get('otherMaterialCharacteristics') == 'ill.'


# series.name: [490$a repetitive]
# series.number: [490$v repetitive]
def test_marc21_to_series():
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
    data = marc21tojson.do(marc21json)
    assert data.get('series') == [{
        'name': 'Collection One',
        'number': '5'
    }, {
        'name': 'Collection Two',
        'number': '123'
    }]


def test_marc21_to_abstract():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('abstracts')


# notes: [500$a repetitive]
def test_marc21_to_notes():
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
    data = marc21tojson.do(marc21json)
    assert data.get('notes') == ['note 1', 'note 2']


# is_part_of 773$t
def test_marc21_to_is_part_of():
    """Test dojson is_part_of."""

    marc21xml = """
    <record>
      <datafield tag="773" ind1="1" ind2=" ">
        <subfield code="t">Stuart Hall : critical dialogues</subfield>
        <subfield code="g">411</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('is_part_of') == 'Stuart Hall : critical dialogues'


# subjects: 6xx [duplicates could exist between several vocabularies,
# if possible deduplicate]
def test_marc21_to_subjects():
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
    data = marc21tojson.do(marc21json)
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

    # 600 without source
    marc21xml = """
    <record>
      <datafield tag="600" ind1=" " ind2=" ">
        <subfield code="a">subject 600 1 ; subject 600 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('subjects')


def test_marc21_to_identifiedby_from_020():
    """Test dojson identifiedBy from 020."""

    marc21xml = """
    <record>
      <datafield tag="020" ind1=" " ind2=" ">
        <subfield code="z">8124605254</subfield>
      </datafield>
      <datafield tag="020" ind1=" " ind2=" ">
        <subfield code="a">9788124605257 (broché)</subfield>
      </datafield>
      <datafield tag="020" ind1=" " ind2=" ">
        <subfield code="a">9788189997212</subfield>
        <subfield code="q">hbk.</subfield>
        <subfield code="c">£125.00</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Isbn',
        'status': 'invalid or cancelled',
        'value': '8124605254'
    }, {
        'type': 'bf:Isbn',
        'qualifier': 'broché',
        'value': '9788124605257'
    }, {
        'type': 'bf:Isbn',
        'qualifier': 'hbk.',
        'acquisitionTerms': '£125.00',
        'value': '9788189997212'
    }]


def test_marc21_to_identifiedby_from_022():
    """Test dojson identifiedBy from 022."""

    marc21xml = """
    <record>
      <datafield tag="022" ind1=" " ind2=" ">
        <subfield code="a">0264-2875</subfield>
        <subfield code="l">0264-2875</subfield>
      </datafield>
      <datafield tag="022" ind1=" " ind2=" ">
        <subfield code="a">0264-2875</subfield>
        <subfield code="y">0080-4649</subfield>
      </datafield>
      <datafield tag="022" ind1=" " ind2=" ">
        <subfield code="m">0080-4650</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Issn',
        'value': '0264-2875'
    }, {
        'type': 'bf:IssnL',
        'value': '0264-2875'
    }, {
        'type': 'bf:Issn',
        'value': '0264-2875'
    }, {
        'type': 'bf:Issn',
        'status': 'invalid',
        'value': '0080-4649'
    }, {
        'type': 'bf:IssnL',
        'status': 'cancelled',
        'value': '0080-4650'
    }]


def test_marc21_to_identifiedby_from_024_snl_bnf():
    """Test dojson identifiedBy from 024 field snl and bnf."""
    marc21xml = """
    <record>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">http://permalink.snl.ch/bib/chccsa86779</subfield>
        <subfield code="2">permalink</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">http://catalogue.bnf.fr/ark:/12148/cb312v</subfield>
        <subfield code="2">uri</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type':
        'uri',
        'source':
        'SNL',
        'value':
        'http://permalink.snl.ch/bib/chccsa86779'
    }, {
        'type':
        'uri',
        'source':
        'BNF',
        'value':
        'http://catalogue.bnf.fr/ark:/12148/cb312v'
    }]


def test_marc21_to_identifiedby_from_024_with_subfield_2():
    """Test dojson identifiedBy from 024 field with subfield 2."""

    marc21xml = """
    <record>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">10.1007/978-3-540-37973-7</subfield>
        <subfield code="c">£125.00</subfield>
        <subfield code="d">note</subfield>
        <subfield code="2">doi</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">urn:nbn:de:101:1-201609052530</subfield>
        <subfield code="2">urn</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">NIPO 035-16-060-7</subfield>
        <subfield code="2">nipo</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">7290105422026</subfield>
        <subfield code="2">danacode</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">VD18 10153438</subfield>
        <subfield code="2">vd18</subfield>
      </datafield>
      <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="a">00028947969525</subfield>
        <subfield code="2">gtin-14</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Doi',
        'value': '10.1007/978-3-540-37973-7',
        'acquisitionTerms': '£125.00',
        'note': 'note'
    }, {
        'type':
        'bf:Urn',
        'value':
        'urn:nbn:de:101:1-201609052530'
    }, {
        'type': 'bf:Local',
        'source': 'NIPO',
        'value': 'NIPO 035-16-060-7'
    }, {
        'type': 'bf:Local',
        'source': 'danacode',
        'value': '7290105422026'
    }, {
        'type': 'bf:Local',
        'source': 'vd18',
        'value': 'VD18 10153438'
    }, {
        'type': 'bf:Gtin14Number',
        'value': '00028947969525'
    }]


def test_marc21_to_identifiedby_from_024_without_subfield_2():
    """Test dojson identifiedBy from 024 field without subfield 2."""

    marc21xml = """
    <record>
      <datafield tag="024" ind1=" " ind2=" ">
        <subfield code="a">9782100745463</subfield>
      </datafield>
      <datafield tag="024" ind1="0" ind2="1">
        <subfield code="a">702391010582 (vol. 2) </subfield>
      </datafield>
      <datafield tag="024" ind1="0" ind2="2">
        <subfield code="a">Erato ECD 88030</subfield>
      </datafield>
      <datafield tag="024" ind1="1" ind2=" ">
        <subfield code="a">604907014223 (vol. 5)</subfield>
      </datafield>
      <datafield tag="024" ind1="1" ind2="2">
        <subfield code="a">EMI Classics 5 55585 2</subfield>
      </datafield>
      <datafield tag="024" ind1="2" ind2=" ">
        <subfield code="a">M006546565 (kritischer B., kartoniert)</subfield>
        <subfield code="q">vol. 1</subfield>
      </datafield>
      <datafield tag="024" ind1="2" ind2=" ">
        <subfield code="a">9790201858135</subfield>
        <subfield code="q">Kritischer Bericht</subfield>
      </datafield>
      <datafield tag="024" ind1="2" ind2=" ">
        <subfield code="a">4018262101065 (Bd. 1)</subfield>
      </datafield>
      <datafield tag="024" ind1="3" ind2=" ">
        <subfield code="a">309-5-56-196162-1</subfield>
        <subfield code="q">CD audio classe</subfield>
      </datafield>
      <datafield tag="024" ind1="3" ind2=" ">
        <subfield code="a">9783737407427</subfield>
        <subfield code="q">Bd 1</subfield>
        <subfield code="q">pbk.</subfield>
      </datafield>
      <datafield tag="024" ind1="3" ind2="2">
        <subfield code="a">EP 2305</subfield>
      </datafield>
      <datafield tag="024" ind1="3" ind2="2">
        <subfield code="a">97 EP 1234</subfield>
      </datafield>
     <datafield tag="024" ind1="8" ind2=" ">
        <subfield code="a">ELC1283925</subfield>
      </datafield>
      <datafield tag="024" ind1="8" ind2=" ">
        <subfield code="a">0000-0002-A3B1-0000-0-0000-0000-2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Identifier',
        'value': '9782100745463'
    }, {
        'type': 'bf:Isrc',
        'qualifier': 'vol. 2',
        'value': '702391010582'
    }, {
        'type': 'bf:Isrc',
        'value': 'Erato ECD 88030'
    }, {
        'type': 'bf:Upc',
        'qualifier': 'vol. 5',
        'value': '604907014223'
    }, {
        'type': 'bf:Upc',
        'value': 'EMI Classics 5 55585 2'
    }, {
        'type': 'bf:Ismn',
        'qualifier': 'kritischer B., kartoniert, vol. 1',
        'value': 'M006546565'
    }, {
        'type': 'bf:Ismn',
        'qualifier': 'Kritischer Bericht',
        'value': '9790201858135'
    }, {
        'type': 'bf:Identifier',
        'qualifier': 'Bd. 1',
        'value': '4018262101065'
    }, {
        'type': 'bf:Identifier',
        'qualifier': 'CD audio classe',
        'value': '309-5-56-196162-1'
    }, {
        'type': 'bf:Ean',
        'qualifier': 'Bd 1, pbk.',
        'value': '9783737407427'
    }, {
        'type': 'bf:Identifier',
        'value': 'EP 2305'
    }, {
        'type': 'bf:Ean',
        'value': '97 EP 1234'
    }, {
        'type': 'bf:Identifier',
        'value': 'ELC1283925'
    }, {
        'type':
        'bf:Isan',
        'value':
        '0000-0002-A3B1-0000-0-0000-0000-2'
    }]


def test_marc21_to_identifiedby_from_028():
    """Test dojson identifiedBy from 035."""

    marc21xml = """
    <record>
      <datafield tag="028" ind1="3" ind2=" ">
        <subfield code="a">1234</subfield>
        <subfield code="b">SRC</subfield>
        <subfield code="q">Qualif1</subfield>
        <subfield code="q">Qualif2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:MusicPublisherNumber',
        'source': 'SRC',
        'qualifier': 'Qualif1, Qualif2',
        'value': '1234'
    }]

    marc21xml = """
    <record>
      <datafield tag="028" ind1="9" ind2=" ">
        <subfield code="a">1234</subfield>
        <subfield code="b">SRC</subfield>
        <subfield code="q">Qualif1</subfield>
        <subfield code="q">Qualif2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Identifier',
        'source': 'SRC',
        'qualifier': 'Qualif1, Qualif2',
        'value': '1234'
    }]


def test_marc21_to_identifiedby_from_035():
    """Test dojson identifiedBy from 035."""

    marc21xml = """
    <record>
      <datafield tag="035" ind1=" " ind2=" ">
        <subfield code="a">R008945501</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'RERO',
        'value': 'R008945501'
    }]


def test_marc21_to_identifiedby_from_930():
    """Test dojson identifiedBy from 930."""

    # identifier with source in parenthesis
    marc21xml = """
    <record>
      <datafield tag="930" ind1=" " ind2=" ">
        <subfield code="a">(OCoLC) ocm11113722</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'OCoLC',
        'value': 'ocm11113722'
    }]
    # identifier without source in parenthesis
    marc21xml = """
    <record>
      <datafield tag="930" ind1=" " ind2=" ">
        <subfield code="a">ocm11113722</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'value': 'ocm11113722'
    }]


@mock.patch('requests.get')
def test_get_person_link(mock_get, capsys):
    """Test get mef person link"""
    mock_get.return_value = mock_response(
        json_data={'hits': {
            'hits': [{
                'links': {
                    'self': 'mocked_url'
                }
            }]
        }})
    mef_url = get_person_link(bibid='1',
                              id='(RERO)A003945843',
                              key='100..',
                              value={'0': '(RERO)A003945843'})
    assert mef_url == 'mocked_url'

    os.environ['RERO_ILS_MEF_URL'] = 'https://mefdev.test.rero.ch/api/mef'
    mef_url = get_person_link(bibid='1',
                              id='(RERO)A003945843',
                              key='100..',
                              value={'0': '(RERO)A003945843'})
    assert mef_url == 'mocked_url'

    mock_get.return_value = mock_response(status=400)
    mef_url = get_person_link(bibid='1',
                              id='(RERO)A123456789',
                              key='100..',
                              value={'0': '(RERO)A123456789'})
    assert not mef_url
    out, err = capsys.readouterr()
    assert err == "ERROR MEF REQUEST:\t1\t" + \
        'https://mefdev.test.rero.ch/api/mef/?q=rero.pid:A123456789\t400\t\n'

    mock_get.return_value = mock_response(status=400)
    mef_url = get_person_link(bibid='1',
                              id='X123456789',
                              key='100..',
                              value={'0': 'X123456789'})
    assert not mef_url
    out, err = capsys.readouterr()
    assert err == 'WARNING NOT MEF REF:\t1\tX123456789\t100..\t' + \
        "{'0': 'X123456789'}\t\n"


def test_marc21_to_files():
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
    data = marc21tojson.do(marc21json)
    assert len(data.get('files')) == 1
    assert data.get('files')[0]['key'] == 'file.pdf'
    assert data.get('files')[0]['url'] == 'http://some.url/file.pdf'
    assert data.get('files')[0]['label'] == 'Dépliant de l\'exposition'
    assert data.get('files')[0]['order'] == 1


def test_marc21_to_other_edition():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('otherEdition')


def test_marc21_to_specific_collection():
    """Test extracting collection from file 982."""
    # Extract collection OK
    marc21xml = """
    <record>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Treize étoiles</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('specificCollections') == ['Treize étoiles']

    # Multiple collections
    marc21xml = """
    <record>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Collection 1</subfield>
        </datafield>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="a">Collection 2</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('specificCollections') == ['Collection 1', 'Collection 2']

    # No code a
    marc21xml = """
    <record>
        <datafield tag="982" ind1=" " ind2=" ">
            <subfield code="b">Treize étoiles</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data.get('specificCollections')

    # Not field 982
    marc21xml = """
    <record>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data.get('specificCollections')
