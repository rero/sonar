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

"""Test documents views."""

import pytest
from flask import g, url_for

import sonar.modules.documents.views as views
from sonar.modules.documents.api import DocumentRecord


def test_pull_ir(app):
    """Test pull IR."""
    views.pull_ir(None, {"ir": "sonar"})


def test_index(client):
    """Test frontpage."""
    assert isinstance(views.index(), str)
    assert client.get('/').status_code == 200


def test_search(app, client):
    """Test search."""
    assert isinstance(views.search(), str)
    assert client.get(
        '/organization/sonar/search/documents').status_code == 200


def test_detail(app, client, document_fixture):
    """Test document detail page."""
    assert client.get('/organization/sonar/documents/10000').status_code == 200


def test_title_format(document_fixture):
    """Test title format for display it in template."""
    # No title
    assert views.title_format({'mainTitle': [], 'subtitle': []}, 'en') == ''

    # Take the first one as fallback
    assert views.title_format(
        {'mainTitle': [{
            'language': 'spa',
            'value': 'Title ES'
        }]}, 'fr') == 'Title ES'

    title = {
        'mainTitle': [{
            'language': 'ger',
            'value': 'Title DE'
        }, {
            'language': 'eng',
            'value': 'Title EN'
        }, {
            'language': 'fre',
            'value': 'Title FR'
        }],
        'subtitle': [{
            'language': 'ita',
            'value': 'Subtitle IT'
        }, {
            'language': 'fre',
            'value': 'Subtitle FR'
        }, {
            'language': 'eng',
            'value': 'Subtitle EN'
        }]
    }

    assert views.title_format(title, 'en') == 'Title EN : Subtitle EN'
    assert views.title_format(title, 'fr') == 'Title FR : Subtitle FR'
    assert views.title_format(title, 'de') == 'Title DE : Subtitle EN'
    assert views.title_format(title, 'it') == 'Title EN : Subtitle IT'


def test_authors_format(document_fixture):
    """Test author format filter."""
    assert views.authors_format(
        '10000', 'en'
    ) == 'Mancini, Loriano, Librarian, 1975-03-23; Ronchetti, Elvezio; ' \
         'Trojani, Fabio'


def test_publishers_format():
    """Test publishers format."""
    result = 'Foo; place1; place2: Foo; Bar'
    assert result == views.publishers_format([{
        'name': ['Foo']
    }, {
        'place': ['place1', 'place2'],
        'name': ['Foo', 'Bar']
    }])


def test_series_format():
    """Test series format."""
    result = 'serie 1; serie 2, 2018'
    assert result == views.series_format([{
        'name': 'serie 1'
    }, {
        'name': 'serie 2',
        'number': '2018'
    }])


def test_abstracts_format():
    """Test series format."""
    abstracts = [{
        'language': 'eng',
        'value': 'Abstract'
    }, {
        'language': 'fre',
        'value': 'Résumé'
    }]

    result = 'Abstract\n\nRésumé'
    assert result == views.abstracts_format(abstracts)


def test_subjects_format(document_fixture):
    """Test subjects format."""
    subjects = [{
        'label': {
            'value': ['subject 1', 'subject 2'],
            'language': 'eng'
        }
    }, {
        'label': {
            'value': ['sujet 1', 'sujet 2'],
            'language': 'fre'
        }
    }, {
        'label': {
            'value': ['subject with source 1', 'subject with source 2']
        },
        'source': 'RERO'
    }]

    assert views.subjects_format(subjects, 'en') == [{
        'value':
        'subject 1 ; subject 2'
    }, {
        'value': 'subject with source 1 ; subject with source 2',
        'source': 'RERO'
    }]

    assert views.subjects_format(subjects, 'de') == [{
        'value': 'subject with source 1 ; subject with source 2',
        'source': 'RERO'
    }]


def test_identifiedby_format():
    """Test identifiedBy format."""
    identifiedby = [{
        'type': 'bf:Local',
        'source': 'RERO',
        'value': 'R008745599'
    }, {
        'type': 'bf:Isbn',
        'value': '9782844267788'
    }, {
        'type': 'bf:Local',
        'source': 'BNF',
        'value': 'FRBNF452959040000002'
    }, {
        'type': 'uri',
        'value': 'http://catalogue.bnf.fr/ark:/12148/cb45295904f'
    }]
    results = [{
        'type': 'Isbn',
        'value': '9782844267788'
    }, {
        'type': 'uri',
        'value': 'http://catalogue.bnf.fr/ark:/12148/cb45295904f'
    }]
    assert results == views.identifiedby_format(identifiedby)


def test_create_publication_statement(document_fixture):
    """Test create publication statement."""
    publication_statement = views.create_publication_statement(
        document_fixture['provisionActivity'][0])
    assert publication_statement
    assert publication_statement[
        'default'] == 'Bienne : Impr. Weber, [2006] ; Lausanne ; Rippone : ' \
                      'Impr. Coustaud'


def test_nl2br():
    """Test nl2br conversion."""
    text = 'Multiline text\nMultiline text'
    assert views.nl2br(text) == 'Multiline text<br>Multiline text'


def test_edition_format(document_fixture):
    """Test edition format."""
    edition_format = views.edition_format(document_fixture['editionStatement'])
    assert len(edition_format) == 2
    assert edition_format[0] == 'Di 3 ban / Zeng Lingliang zhu bian'


def test_get_code_from_bibliographic_language(app):
    """Test bibliographic language code to alpha 2 code conversion."""
    assert views.get_language_from_bibliographic_code('ger') == 'de'

    with pytest.raises(Exception) as e:
        views.get_language_from_bibliographic_code('zzz')
    assert str(e.value) == 'Language code not found for "zzz"'


def test_get_bibliographic_code_from_language(app):
    """Test bibliographic language code to alpha 2 code conversion."""
    with pytest.raises(Exception) as e:
        views.get_bibliographic_code_from_language("zz")
    assert str(e.value) == 'Language code not found for "zz"'

    assert views.get_bibliographic_code_from_language('de') == 'ger'


def test_get_preferred_languages(app):
    """Test getting the list of prefererred languages."""
    assert views.get_preferred_languages() == ['eng', 'fre', 'ger', 'ita']
    assert views.get_preferred_languages('fre') == ['fre', 'eng', 'ger', 'ita']
