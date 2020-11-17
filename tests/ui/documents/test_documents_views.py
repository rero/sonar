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


def test_default_view_code(app):
    """Test set default view code."""
    views.default_view_code(None, {'view': 'global'})


def test_store_organisation(client, db, organisation):
    """Test store organisation in globals."""
    # Default view, no organisation stored.
    assert client.get(url_for('documents.index',
                              view='global')).status_code == 200
    assert not g.get('organisation')

    # Existing organisation stored, with shared view
    assert client.get(url_for('documents.index',
                              view='org')).status_code == 200
    assert g.organisation['code'] == 'org'
    assert g.organisation['isShared']

    # Non-existing organisation
    g.pop('organisation')
    assert client.get(url_for('documents.index',
                              view='non-existing')).status_code == 404
    assert not g.get('organisation')

    # Existing organisation without shared view
    organisation['isShared'] = False
    organisation.commit()
    db.session.commit()
    assert client.get(url_for('documents.index',
                              view='org')).status_code == 404
    assert not g.get('organisation')


def test_index(client):
    """Test frontpage."""
    assert isinstance(views.index(), str)
    assert client.get('/').status_code == 200


def test_search(app, client):
    """Test search."""
    assert isinstance(views.search(), str)
    assert client.get(url_for('documents.search',
                              resource_type='documents')).status_code == 200


def test_detail(app, client, document_with_file):
    """Test document detail page."""
    assert client.get(
        url_for('documents.detail',
                pid_value=document_with_file['pid'])).status_code == 200

    assert client.get(url_for('documents.detail',
                              pid_value='not-existing')).status_code == 404


def test_title_format(document):
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


def test_create_publication_statement(document):
    """Test create publication statement."""
    publication_statement = views.create_publication_statement(
        document['provisionActivity'][0])
    assert publication_statement
    assert publication_statement[
        'default'] == 'Bienne : Impr. Weber, [2006] ; Lausanne ; Rippone : ' \
                      'Impr. Coustaud'


def test_nl2br():
    """Test nl2br conversion."""
    text = 'Multiline text\nMultiline text'
    assert views.nl2br(text) == 'Multiline text<br>Multiline text'


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


def test_file_size(app):
    """Test converting file size to a human readable size."""
    assert views.file_size(2889638) == '2.76Mb'


def test_has_external_urls_for_files(app):
    """Test if record has to point files to external URL or not."""
    assert views.has_external_urls_for_files({
        'pid': 1,
        'organisation': {
            'pid': 'csal'
        }
    })

    assert not views.has_external_urls_for_files({
        'pid': 1,
        'organisation': {
            'pid': 'usi'
        }
    })

    assert not views.has_external_urls_for_files({
        'pid': 1,
        'organisation': {}
    })

    assert not views.has_external_urls_for_files({'pid': 1})


def test_part_of_format():
    """Test part of format for displaying."""
    assert views.part_of_format({
        'document': {
            'title': 'Mehr oder weniger Staat?'
        },
        'numberingYear': '2015',
        'numberingVolume': '28',
        'numberingIssue': '2',
        'numberingPages': '469-480'
    }) == 'Mehr oder weniger Staat?, 2015, vol. 28, no. 2, p. 469-480'

    assert views.part_of_format({
        'document': {
            'title': 'Mehr oder weniger Staat?'
        },
        'numberingYear': '2015',
        'numberingIssue': '2',
        'numberingPages': '469-480'
    }) == 'Mehr oder weniger Staat?, 2015'

    assert views.part_of_format({
        'numberingYear': '2015',
    }) == '2015'


def test_abstracts(app):
    """Test getting ordered abstracts."""
    # Abstracts are ordered, english first.
    abstracts = [{
        'language': 'fre',
        'value': 'Résumé'
    }, {
        'language': 'eng',
        'value': 'Summary'
    }]
    assert views.abstracts({'abstracts': abstracts})[0]['language'] == 'eng'

    # No abstract
    assert views.abstracts({}) == []


def test_contributors():
    """Test ordering contributors."""
    contributors = [{
        'role': ['dgs']
    }, {
        'role': ['ctb']
    }, {
        'role': ['prt']
    }, {
        'role': ['edt']
    }, {
        'role': ['cre']
    }]

    priorities = ['cre', 'ctb', 'dgs', 'edt', 'prt']

    for index, contributor in enumerate(
            views.contributors({'contribution': contributors})):
        assert contributor['role'][0] == priorities[index]

    # No contributors
    assert views.contributors({}) == []


def test_dissertation():
    """Test formatting of dissertation text."""
    # No dissertation
    assert not views.dissertation({})

    # Only degree property
    assert views.dissertation(
        {'dissertation': {
            'degree': 'Thèse de doctorat'
        }}) == 'Thèse de doctorat'

    #  With jury notes
    assert views.dissertation({
        'dissertation': {
            'degree': 'Thèse de doctorat',
            'jury_note': 'Jury note'
        }
    }) == 'Thèse de doctorat (jury note: Jury note)'

    # With granting institution
    assert views.dissertation(
        {
            'dissertation': {
                'degree': 'Thèse de doctorat',
                'jury_note': 'Jury note',
                'grantingInstitution': 'Università della Svizzera italiana'
            }
        }
    ) == 'Thèse de doctorat: Università della Svizzera italiana (jury note: ' \
         'Jury note)'

    # With date
    assert views.dissertation(
        {
            'dissertation': {
                'degree': 'Thèse de doctorat',
                'jury_note': 'Jury note',
                'grantingInstitution': 'Università della Svizzera italiana',
                'date': '2010-01-01'
            }
        }
    ) == 'Thèse de doctorat: Università della Svizzera italiana, 01.01.2010 ' \
         '(jury note: Jury note)'


def test_contribution_text():
    """Test contribution text formatting."""
    # Just creator
    assert views.contribution_text({
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'John Doe'
        },
        'role': ['cre']
    }) == 'John Doe'

    # Contributor
    assert views.contribution_text({
        'agent': {
            'type': 'bf:Person',
            'preferred_name': 'John Doe'
        },
        'role': ['ctb']
    }) == 'John Doe (contribution_role_ctb)'

    # Meeting with only number
    assert views.contribution_text({
        'agent': {
            'type': 'bf:Meeting',
            'preferred_name': 'Meeting',
            'number': '1234'
        }
    }) == 'Meeting (1234)'

    # Meeting with number and date
    assert views.contribution_text({
        'agent': {
            'type': 'bf:Meeting',
            'preferred_name': 'Meeting',
            'number': '1234',
            'date': '2019',
        }
    }) == 'Meeting (1234 : 2019)'

    # Meeting with number, date and place
    assert views.contribution_text({
        'agent': {
            'type': 'bf:Meeting',
            'preferred_name': 'Meeting',
            'number': '1234',
            'date': '2019',
            'place': 'Place'
        }
    }) == 'Meeting (1234 : 2019 : Place)'


def test_project_detail(app, client, project):
    """Test project detail page."""
    assert client.get(url_for('documents.project_detail',
                              pid_value=project['pid'])).status_code == 200

    assert client.get(url_for('documents.project_detail',
                              pid_value='not-existing')).status_code == 404
