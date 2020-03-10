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

import pytest
from dojson.contrib.marc21.utils import create_record
from utils import mock_response

from sonar.modules.documents.dojson.contrib.marc21tojson import marc21tojson
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


def test_get_affiliations():
    """Test getting controlled affiliations."""
    affiliation = '''
    Institute for Research in Biomedicine (IRB), Faculty of Biomedical
    Sciences, Università della Svizzera italiana, Switzerland - Graduate
    School for Cellular and Biomedical Sciences, University of Bern, c/o
    Theodor Kocher Institute, Freiestrasse 1, P.O. Box 938, CH-3000 Bern 9,
    Switzerland
    '''
    affiliations = marc21tojson.get_affiliations(affiliation)
    assert affiliations == [
        'Uni of Bern and Hospital', 'Uni of Italian Switzerland'
    ]

    affiliations = marc21tojson.get_affiliations(None)
    assert not affiliations


def test_load_affiliations():
    """Test load affiliations from file."""
    marc21tojson.load_affiliations()
    assert len(marc21tojson.affiliations) == 77


def test_marc21_to_type_and_institution(app):
    """Test type and institution."""

    # Type and institution
    marc21xml = """
    <record>
        <datafield tag="980" ind1=" " ind2=" ">
            <subfield code="a">BOOK</subfield>
            <subfield code="b">BAAGE</subfield>
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


def test_marc21_to_provision_activity_manufacture_date():
    """Test dojson publication statement.
    - 1 manufacture place and 1 agent, 1 manufacture date
    """

    marc21xml = """
      <record>
        <controlfield tag=
          "008">070518s20062010sz ||| |  ||||00|  |fre d</controlfield>
        <datafield tag="041" ind1="0" ind2=" ">
          <subfield code="a">fre</subfield>
          <subfield code="a">ger</subfield>
        </datafield>
        <datafield tag="260" ind1=" " ind2="3">
          <subfield code="a">Bienne :</subfield>
          <subfield code="b">Impr. Weber</subfield>
          <subfield code="c">[2006]</subfield>
        </datafield>
        <datafield tag="260" ind1=" " ind2="4">
          <subfield code="c">© 2006</subfield>
        </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'statement': [{
            'type': 'bf:Place',
            'label': [{
                'value': 'Bienne'
            }]
        }, {
            'type': 'bf:Agent',
            'label': [{
                'value': 'Impr. Weber'
            }]
        }, {
            'label': [{
                'value': '[2006]'
            }],
            'type': 'Date'
        }],
        'startDate':
        '2006',
        'endDate':
        '2010',
        'place': [{
            'country': 'sz',
            'type': 'bf:Place'
        }]
    }, {
        'type':
        'bf:Publication',
        'statement': [{
            'label': [{
                'value': '© 2006'
            }],
            'type': 'Date'
        }],
        'startDate':
        '2006',
        'endDate':
        '2010',
        'place': [{
            'country': 'sz',
            'type': 'bf:Place'
        }]
    }]


def test_marc21_to_provision_activity_canton():
    """Test dojson publication statement.
    - get canton from field 044
    - 3 publication places and 3 agents from one field 264
    """

    marc21xml = """
      <record>
        <controlfield tag=
          "008">070518s20062010sz ||| |  ||||00|  |fre d</controlfield>
        <datafield tag="041" ind1="0" ind2=" ">
          <subfield code="a">fre</subfield>
          <subfield code="a">ger</subfield>
        </datafield>
        <datafield tag="044" ind1=" " ind2=" ">
          <subfield code="a">sz</subfield>
          <subfield code="c">ch-be</subfield>
        </datafield>
        <datafield tag="260" ind1=" " ind2="1">
          <subfield code="a">Biel/Bienne :</subfield>
          <subfield code="b">Centre PasquArt ;</subfield>
          <subfield code="a">Nürnberg :</subfield>
          <subfield code="b">Verlag für Moderne Kunst ;</subfield>
          <subfield code="a">Manchester :</subfield>
          <subfield code="b">distrib. in the United Kingdom [etc.],</subfield>
          <subfield code="c">[2006-2010]</subfield>
        </datafield>
        <datafield tag="260" ind1=" " ind2="3">
          <subfield code="a">Bienne :</subfield>
          <subfield code="b">Impr. Weber</subfield>
        </datafield>
        <datafield tag="260" ind1=" " ind2="4">
          <subfield code="c">© 2006</subfield>
        </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)

    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'statement': [{
            'type': 'bf:Place',
            'label': [{
                'value': 'Biel/Bienne'
            }]
        }, {
            'type': 'bf:Agent',
            'label': [{
                'value': 'Centre PasquArt'
            }]
        }, {
            'type': 'bf:Place',
            'label': [{
                'value': 'Nürnberg'
            }]
        }, {
            'type': 'bf:Agent',
            'label': [{
                'value': 'Verlag für Moderne Kunst'
            }]
        }, {
            'type': 'bf:Place',
            'label': [{
                'value': 'Manchester'
            }]
        }, {
            'type':
            'bf:Agent',
            'label': [{
                'value': 'distrib. in the United Kingdom [etc.]'
            }]
        }, {
            'label': [{
                'value': '[2006-2010]'
            }],
            'type': 'Date'
        }],
        'startDate':
        '2006',
        'endDate':
        '2010',
        'place': [{
            'canton': 'be',
            'country': 'sz',
            'type': 'bf:Place'
        }]
    }, {
        'type':
        'bf:Publication',
        'statement': [{
            'type': 'bf:Place',
            'label': [{
                'value': 'Bienne'
            }]
        }, {
            'type': 'bf:Agent',
            'label': [{
                'value': 'Impr. Weber'
            }]
        }],
        'startDate':
        '2006',
        'endDate':
        '2010',
        'place': [{
            'canton': 'be',
            'country': 'sz',
            'type': 'bf:Place'
        }]
    }, {
        'type':
        'bf:Publication',
        'statement': [{
            'label': [{
                'value': '© 2006'
            }],
            'type': 'Date'
        }],
        'startDate':
        '2006',
        'endDate':
        '2010',
        'place': [{
            'canton': 'be',
            'country': 'sz',
            'type': 'bf:Place'
        }]
    }]


def test_marc21_to_provision_activity_1_place_2_agents():
    """Test dojson publication statement.
    - 1 publication place and 2 agents from one field 264
    """

    marc21xml = """
      <record>
        <controlfield tag=
          "008">940202m19699999fr |||||| ||||00|| |fre d</controlfield>
        <datafield tag="260" ind1=" " ind2="1">
          <subfield code="a">[Paris] :</subfield>
          <subfield code="b">Desclée de Brouwer [puis]</subfield>
          <subfield code="b">Etudes augustiniennes,</subfield>
          <subfield code="c">1969-</subfield>
        </datafield>
      </record>
     """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'fr',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': '[Paris]'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': 'Desclée de Brouwer [puis]'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': 'Etudes augustiniennes'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': '1969-'
            }],
            'type': 'Date'
        }],
        'startDate':
        '1969'
    }]


def test_marc21_to_provision_activity_unknown_place_2_agents():
    """Test dojson publication statement.
    - unknown place and 2 agents from one field 264
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">960525s1968    be |||||| ||||00|| |fre d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="a">[Lieu de publication non identifié] :</subfield>
        <subfield code="b">Labor :</subfield>
        <subfield code="b">Nathan,</subfield>
        <subfield code="c">1968</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'be',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': '[Lieu de publication non identifié]'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Labor'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': 'Nathan'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': '1968'
            }],
            'type': 'Date'
        }],
        'startDate':
        '1968'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'default': '[Lieu de publication non identifié] : Labor, Nathan, 1968'
    }


def test_marc21_to_provision_activity_3_places_dann_2_agents():
    """Test dojson publication statement.
    - 3 places and 2 agents from one field 264
    - 2 places with [dann] prefix
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">000927m19759999gw |||||| ||||00|  |ger d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="a">Hamm (Westf.) ;</subfield>
        <subfield code="a">[dann] Herzberg ;</subfield>
        <subfield code="a">[dann] Nordhausen :</subfield>
        <subfield code="b">T. Bautz,</subfield>
        <subfield code="c">1975-</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'gw',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Hamm (Westf.)'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': '[dann] Herzberg'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': '[dann] Nordhausen'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': 'T. Bautz'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': '1975-'
            }],
            'type': 'Date'
        }],
        'startDate':
        '1975'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'default':
        'Hamm (Westf.) ; [dann] Herzberg ; [dann] Nordhausen : ' +
        'T. Bautz, 1975-'
    }


def test_marc21_to_provision_activity_2_places_1_agent():
    """Test dojson publication statement.
    - 2 publication places and 1 agents from one field 264
    """

    marc21xml = """
      <record>
      <controlfield tag=
        "008">960525s1966    sz |||||| ||||00|| |fre d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="a">[Louvain] ;</subfield>
        <subfield code="a">[Paris] :</subfield>
        <subfield code="b">[éditeur non identifié],</subfield>
        <subfield code="c">[1966]</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'sz',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': '[Louvain]'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': '[Paris]'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': '[éditeur non identifié]'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': '[1966]'
            }],
            'type': 'Date'
        }],
        'startDate':
        '1966'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'default': '[Louvain] ; [Paris] : [éditeur non identifié], [1966]'
    }


def test_marc21_to_provision_activity_1_place_1_agent_reprint_date():
    """Test dojson publication statement.
    - 1 place and 1 agent from one field 264
    - reprint date in 008
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">000918r17581916xxu|||||| ||||00|| |eng d</controlfield>
      <datafield tag="041" ind1="0" ind2=" ">
        <subfield code="a">eng</subfield>
        <subfield code="a">fre</subfield>
      </datafield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="a">Washington :</subfield>
        <subfield code="b">Carnegie Institution of Washington,</subfield>
        <subfield code="c">1916</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'xxu',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Washington'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': 'Carnegie Institution of Washington'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': '1916'
            }],
            'type': 'Date'
        }],
        'startDate':
        '1758',
        'endDate':
        '1916'
    }]


def test_marc21_to_provision_activity_1_place_1_agent_uncertain_date():
    """Test dojson publication statement.
    - 1 place and 1 agent from one field 264
    - uncertain date
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">160126q1941    fr ||| |  ||||00|  |fre d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="a">Aurillac :</subfield>
        <subfield code="b">Impr. moderne,</subfield>
        <subfield code="c">[1941?]</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'fr',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Aurillac'
            }],
            'type': 'bf:Place'
        }, {
            'label': [{
                'value': 'Impr. moderne'
            }],
            'type': 'bf:Agent'
        }, {
            'label': [{
                'value': '[1941?]'
            }],
            'type': 'Date'
        }],
        'note':
        'Date(s) incertaine(s) ou inconnue(s)',
        'startDate':
        '1941'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'default': 'Aurillac : Impr. moderne, [1941?]'
    }


def test_marc21_to_provision_activity_1_place_1_agent_chi_hani():
    """Test dojson publication statement.
    - 1 place and 1 agent from one field 264
    - extract data from the linked 880 from 3 fields 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |chi d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="6">880-04</subfield>
        <subfield code="a">Beijing :</subfield>
        <subfield code="b">Beijing da xue chu ban she,</subfield>
        <subfield code="c">2017</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2="1">
        <subfield code="6">264-04/$1</subfield>
        <subfield code="a">北京 :</subfield>
        <subfield code="b">北京大学出版社,</subfield>
        <subfield code="c">2017</subfield>
      </datafield>
      <datafield tag="880" ind1="1" ind2=" ">
        <subfield code="6">100-01/$1</subfield>
        <subfield code="a">余锋</subfield>
      </datafield>
      <datafield tag="880" ind1="1" ind2="0">
        <subfield code="6">245-02/$1</subfield>
        <subfield code="a">中国娱乐法 /</subfield>
        <subfield code="c">余锋著</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'cc',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Beijing'
            }, {
                'value': '北京',
                'language': 'chi-hani'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Beijing da xue chu ban she'
            }, {
                'value': '北京大学出版社',
                'language': 'chi-hani'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': '2017'
            }, {
                'language': 'chi-hani',
                'value': '2017'
            }],
            'type':
            'Date'
        }],
        'startDate':
        '2017'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'chi-hani': '北京 : 北京大学出版社, 2017',
        'default': 'Beijing : Beijing da xue chu ban she, 2017'
    }
    marc21xml = """
      <record>
      <controlfield tag=
        "008">180323s2017    cc ||| |  ||||00|  |eng d</controlfield>
      <datafield tag="260" ind1=" " ind2="1">
        <subfield code="6">880-04</subfield>
        <subfield code="a">Beijing :</subfield>
        <subfield code="b">Beijing da xue chu ban she,</subfield>
        <subfield code="c">2017</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2="1">
        <subfield code="6">264-04/$1</subfield>
        <subfield code="a">北京 :</subfield>
        <subfield code="b">北京大学出版社,</subfield>
        <subfield code="c">2017</subfield>
      </datafield>
      <datafield tag="880" ind1="1" ind2=" ">
        <subfield code="6">100-01/$1</subfield>
        <subfield code="a">余锋</subfield>
      </datafield>
      <datafield tag="880" ind1="1" ind2="0">
        <subfield code="6">245-02/$1</subfield>
        <subfield code="a">中国娱乐法 /</subfield>
        <subfield code="c">余锋著</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'cc',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Beijing'
            }, {
                'value': '北京',
                'language': 'und-hani'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Beijing da xue chu ban she'
            }, {
                'value': '北京大学出版社',
                'language': 'und-hani'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': '2017'
            }, {
                'language': 'und-hani',
                'value': '2017'
            }],
            'type':
            'Date'
        }],
        'startDate':
        '2017'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'und-hani': '北京 : 北京大学出版社, 2017',
        'default': 'Beijing : Beijing da xue chu ban she, 2017'
    }


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


def test_marc21_to_provision_activity_1_place_1_agent_ara_arab():
    """Test dojson publication statement.
    - 1 place and 1 agent from one field 264
    - extract data from the linked 880
    """
    marc21xml = """
      <record>
      <controlfield tag=
        "008">150617s2014    ua ||| |  ||||00|  |ara d</controlfield>
      <datafield tag="264" ind1=" " ind2="1">
        <subfield code="6">880-01</subfield>
        <subfield code="a">al-Qāhirah :</subfield>
        <subfield code="b">Al-Hayʾat al-ʿāmmah li quṣūr al-thaqāfah,</subfield>
        <subfield code="c">2014</subfield>
      </datafield>
      <datafield tag="880" ind1=" " ind2="1">
        <subfield code="6">264-01/(3/r</subfield>
        <subfield code="a">القاهرة :</subfield>
        <subfield code="b">الهيئة العامة لقصور الثقافة,</subfield>
        <subfield code="c">2014</subfield>
      </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'ua',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'al-Qāhirah'
            }, {
                'value': 'القاهرة',
                'language': 'ara-arab'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Al-Hayʾat al-ʿāmmah li quṣūr al-thaqāfah'
            }, {
                'value': 'الهيئة العامة لقصور الثقافة',
                'language': 'ara-arab'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': '2014'
            }, {
                'value': '2014',
                'language': 'ara-arab'
            }],
            'type':
            'Date'
        }],
        'startDate':
        '2014'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'ara-arab':
        'القاهرة : الهيئة العامة لقصور الثقافة, 2014',
        'default':
        'al-Qāhirah : Al-Hayʾat al-ʿāmmah li quṣūr al-thaqāfah,' + ' 2014'
    }


def test_marc21_to_provision_activity_2_places_2_agents_rus_cyrl():
    """Test dojson publication statement.
    - 2 places and 2 agents from one field 264
    - extract data from the linked 880 from 3 fields 880
    """
    marc21xml = """
      <record>
        <controlfield tag=
          "008">170626s2017    ru ||| |  ||||00|  |rus d</controlfield>
        <datafield tag="264" ind1=" " ind2="1">
          <subfield code="6">880-02</subfield>
          <subfield code="a">Ierusalim :</subfield>
          <subfield code="b">Gesharim ;</subfield>
          <subfield code="a">Moskva :</subfield>
          <subfield code="b">Mosty Kulʹtury,</subfield>
          <subfield code="c">2017</subfield>
        </datafield>
        <datafield tag="264" ind1=" " ind2="4">
          <subfield code="c">©2017</subfield>
        </datafield>
        <datafield tag="880" ind1=" " ind2="1">
          <subfield code="6">264-02/(N</subfield>
          <subfield code="a">Иерусалим :</subfield>
          <subfield code="b">Гешарим ;</subfield>
          <subfield code="a">Москва :</subfield>
          <subfield code="b">Мосты Культуры,</subfield>
          <subfield code="c">2017</subfield>
        </datafield>
        <datafield tag="880" ind1="1" ind2=" ">
          <subfield code="6">490-03/(N</subfield>
          <subfield code="a">Прошлый век. Воспоминания</subfield>
        </datafield>
        <datafield tag="880" ind1="1" ind2="0">
          <subfield code="6">245-01/(N</subfield>
          <subfield code="a">Воспоминания бабушки :</subfield>
          <subfield code=
              "b">очерки культурной истории евреев России в XIX в. /</subfield>
          <subfield code="c">Полина Венгерова</subfield>
        </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'ru',
            'type': 'bf:Place'
        }],
        'statement': [{
            'label': [{
                'value': 'Ierusalim'
            }, {
                'value': 'Иерусалим',
                'language': 'rus-cyrl'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Gesharim'
            }, {
                'value': 'Гешарим',
                'language': 'rus-cyrl'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': 'Moskva'
            }, {
                'value': 'Москва',
                'language': 'rus-cyrl'
            }],
            'type':
            'bf:Place'
        }, {
            'label': [{
                'value': 'Mosty Kulʹtury'
            }, {
                'value': 'Мосты Культуры',
                'language': 'rus-cyrl'
            }],
            'type':
            'bf:Agent'
        }, {
            'label': [{
                'value': '2017'
            }, {
                'language': 'rus-cyrl',
                'value': '2017'
            }],
            'type':
            'Date'
        }],
        'startDate':
        '2017'
    }]
    assert create_publication_statement(data.get('provisionActivity')[0]) == {
        'default': 'Ierusalim : Gesharim ; Moskva : Mosty Kulʹtury, 2017',
        'rus-cyrl': 'Иерусалим : Гешарим ; Москва : Мосты Культуры, 2017'
    }


def test_marc21_to_provision_activity_exceptions(capsys):
    """Test dojson publication statement.
    - exceptions
    """
    marc21xml = """
      <record>
        <controlfield tag=
          "008">170626s2017    ru ||| |  ||||00|  |</controlfield>
        <datafield tag="264" ind1=" " ind2="1">
          <subfield code="6">880-02</subfield>
          <subfield code="a">Ierusalim :</subfield>
        </datafield>
        <datafield tag="880" ind1=" " ind2="1">
          <subfield code="6">264-02/(N</subfield>
          <subfield code="a">Иерусалим :</subfield>
        </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    out, err = capsys.readouterr()
    assert data.get('provisionActivity') == [{
        'type':
        'bf:Publication',
        'place': [{
            'country': 'ru',
            'type': 'bf:Place'
        }],
        'statement': [
            {
                'label': [{
                    'value': 'Ierusalim'
                }, {
                    'value': 'Иерусалим',
                    'language': 'und-zyyy'
                }],
                'type':
                'bf:Place'
            },
        ],
        'startDate':
        '2017'
    }]
    assert err.strip() == ('WARNING LANGUAGE SCRIPTS:\t???\tzyyy\t008:'
                           '\t\t041$a:\t[]\t041$h:\t[]')

    marc21xml = """
      <record>
        <datafield tag="044" ind1=" " ind2=" ">
          <subfield code="c">chbe</subfield>
        </datafield>
      </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    out, err = capsys.readouterr()
    assert err.strip() == 'ERROR INIT CANTONS:\t???\tchbe'


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


def test_marc21_to_identified_by_from_001():
    """Test identifiedBy from 001."""

    marc21xml = """
    <record>
      <controlfield tag="001">327171</controlfield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{
        'type': 'bf:Local',
        'source': 'RERO DOC',
        'value': '327171'
    }]

    marc21xml = "<record></record>"
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_020():
    """Test identifiedBy from 020."""

    marc21xml = """
    <record>
        <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="a">9783796539138</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_024():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_027():
    """Test identifiedBy from 027."""

    marc21xml = """
    <record>
        <datafield tag="027" ind1=" " ind2=" ">
            <subfield code="a">9789027223951</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_035():
    """Test identifiedBy from 035."""

    marc21xml = """
    <record>
        <datafield tag="035" ind1=" " ind2=" ">
            <subfield code="a">R008966083</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_037():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_088():
    """Test identifiedBy from 088."""

    marc21xml = """
    <record>
        <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a">25</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_from_091():
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
    data = marc21tojson.do(marc21json)
    assert data.get('identifiedBy') == [{'type': 'pmid', 'value': '24638240'}]

    # Without code $a
    marc21xml = """
    <record>
        <datafield tag="091" ind1=" " ind2=" ">
            <subfield code="b">pmid</subfield>
        </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('identifiedBy')


def test_marc21_to_identified_by_full():
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
    data = marc21tojson.do(marc21json)
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
        'type': 'pmid',
        'value': '24638240'
    }]


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


def test_marc21_to_contribution_field_100():
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980',
            'date_of_death': '2010'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
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
    data = marc21tojson.do(marc21json)
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
        data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Romagnani, Andrea',
            'date_of_birth': '1980-04-04'
        },
        'role': ['cre'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
    }]


def test_marc21_to_contribution_field_700():
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Piguet, Etienne',
            'date_of_birth': '1980',
            'date_of_death': '2010'
        },
        'role': ['dgs'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution') == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Piguet, Etienne',
            'date_of_birth': '1980'
        },
        'role': ['dgs'],
        'affiliation':
        'University of Bern, Switzerland',
        'controlledAffiliation': ['Uni of Bern and Hospital']
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
        data = marc21tojson.do(marc21json)
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
        data = marc21tojson.do(marc21json)
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
        data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert data.get('contribution')[0]['role'] == ['cre']


def test_marc21_to_contribution_field_710():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('contribution')


def test_marc21_to_contribution_field_711():
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
    data = marc21tojson.do(marc21json)
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
    data = marc21tojson.do(marc21json)
    assert not data.get('contribution')
