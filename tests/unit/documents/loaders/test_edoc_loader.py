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

"""Test edoc record loader."""

import pytest

from sonar.modules.documents.loaders.schemas.edoc import EdocSchema


def test_no_record_metadata():
    """Test when no record data exists."""
    xml = """
<record>
    <header>
        <identifier>oai:edoc.unibas.ch:4</identifier>
    </header>
</record>
    """
    assert not EdocSchema().dump(xml)


def test_language():
    """Test language."""
    # No language --> default
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['language'] == [{
        'type': 'bf:Language',
        'value': 'eng'
    }]

    # One language
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:language>deu</dc:language>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['language'] == [{
        'type': 'bf:Language',
        'value': 'ger'
    }]

    # Multiple languages
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:language>deu</dc:language>
            <dc:language>fra</dc:language>
            <dc:language>eng</dc:language>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['language'] == [{
        'type': 'bf:Language',
        'value': 'ger'
    }, {
        'type': 'bf:Language',
        'value': 'fre'
    }, {
        'type': 'bf:Language',
        'value': 'eng'
    }]


def test_identifiers():
    """Test identifiers."""
    # No specific identifiers
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['identifiedBy'] == [{
        'type': 'bf:Local',
        'source': 'edoc',
        'value': '123456'
    }]

    # All identifiers
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:identifier>specific-id</dc:identifier>
            <dc:identifier>info:doi/10.5451/unibas-001565177</dc:identifier>
            <dc:identifier>info:pmid/1111</dc:identifier>
            <dc:identifier>urn:urn:nbn:ch:bel-bau-diss47638</dc:identifier>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['identifiedBy'] == [{
        'source': 'edoc',
        'type': 'bf:Local',
        'value': '123456'
    }, {
        'type': 'bf:Identifier',
        'value': 'specific-id'
    }, {
        'type':
        'bf:Doi',
        'value':
        '10.5451/unibas-001565177'
    }, {
        'source': 'PMID',
        'type': 'bf:Local',
        'value': '1111'
    }, {
        'type':
        'bf:Urn',
        'value':
        'urn:nbn:ch:bel-bau-diss47638'
    }]


def test_title():
    """Test title."""
    # No title --> default one
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:description>Description</dc:description>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['title'] == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Default title',
            'language': 'eng'
        }]
    }]

    # Only title
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['title'] == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Title',
            'language': 'eng'
        }]
    }]

    # Title + subtitle
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title : Subtitle</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['title'] == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'value': 'Title',
            'language': 'eng'
        }],
        'subtitle': [{
            'value': 'Subtitle',
            'language': 'eng'
        }]
    }]


def test_provision_activity():
    """Test provision activity."""
    # No provision activity
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:description>Description</dc:description>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert 'provisionActivity' not in EdocSchema().dump(xml)

    # Wrong date format
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:date>wrong</dc:date>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert 'provisionActivity' not in EdocSchema().dump(xml)

    # OK
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:date>2019</dc:date>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['provisionActivity'] == [{
        'type': 'bf:Publication',
        'startDate': '2019'
    }]


def test_document_type():
    """Test document type."""
    # No document type --> other
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['documentType'] == 'coar:c_1843'

    # Multiple, takes only the first
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:type>Thesis</dc:type>
            <dc:type>NonPeerReviewed</dc:type>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['documentType'] == 'coar:c_db06'

    # None existing, takes "other"
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:type>Unknown</dc:type>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['documentType'] == 'coar:c_1843'


@pytest.mark.parametrize(
    'document_type,result',
    [('Book', 'coar:c_2f33'), ('Book Section', 'coar:c_3248'),
     ('Conference', 'coar:c_c94f'), ('Workshop Item', 'coar:c_c94f'),
     ('Research Data', 'coar:c_ddb1'), ('Article', 'coar:c_6501'),
     ('Newspaper', 'coar:c_998f'), ('Magazine Article', 'coar:c_998f'),
     ('Audiovisual Material &amp; Event', 'non_textual_object'),
     ('Preprint', 'coar:c_816b'), ('Thesis', 'coar:c_db06'),
     ('Working Paper', 'coar:c_8042'), ('Other', 'coar:c_1843')])
def test_document_type_mappings(document_type, result):
    """Test document type mappings."""
    xml = f"""
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:type>{document_type}</dc:type>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['documentType'] == result


def test_abstracts():
    """Test abstracts."""
    # No abstract
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert 'abstracts' not in EdocSchema().dump(xml)

    # No abstract
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:description>Description</dc:description>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['abstracts'] == [{
        'language': 'eng',
        'value': 'Description'
    }]


def test_subjects():
    """Test subjects."""
    # No subject
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert 'subjects' not in EdocSchema().dump(xml)

    # One subject
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:subject>Subject 1</dc:subject>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['subjects'] == [{
        'label': {
            'language': 'eng',
            'value': ['Subject 1']
        }
    }]

    # Multiple subjects
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:subject>Subject 1</dc:subject>
            <dc:subject>Subject 2</dc:subject>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['subjects'] == [{
        'label': {
            'language': 'eng',
            'value': ['Subject 1', 'Subject 2']
        }
    }]


def test_contribution():
    """Test contibution."""
    # No contribution
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:title>Title</dc:title>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert 'contribution' not in EdocSchema().dump(xml)

    # OK, one creator, multiple contributors
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:creator>Creator</dc:creator>
            <dc:contributor>Contributor 1</dc:contributor>
            <dc:contributor>Contributor 2</dc:contributor>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['contribution'] == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Creator'
        },
        'role': ['cre']
    }, {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Contributor 1'
        },
        'role': ['ctb']
    }, {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Contributor 2'
        },
        'role': ['ctb']
    }]

    # OK, multiple creators, one contributor
    xml = """
<record>
    <header>
        <identifier>123456</identifier>
    </header>
    <metadata>
        <oai_dc:dc>
            <dc:creator>Creator 1</dc:creator>
            <dc:creator>Creator 2</dc:creator>
            <dc:contributor>Contributor</dc:contributor>
        </oai_dc:dc>
    </metadata>
</record>
    """
    assert EdocSchema().dump(xml)['contribution'] == [{
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Creator 1'
        },
        'role': ['cre']
    }, {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Creator 2'
        },
        'role': ['cre']
    }, {
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'Contributor'
        },
        'role': ['ctb']
    }]
