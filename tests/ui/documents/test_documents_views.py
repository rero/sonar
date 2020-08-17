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

import datetime

import pytest
from flask import g, url_for

import sonar.modules.documents.views as views


def test_default_view_code(app):
    """Test set default view code."""
    views.default_view_code(None, {'view': 'global'})


def test_store_organisation(db, organisation):
    """Test store organisation in globals."""
    # Default view, no organisation stored.
    views.store_organisation(None, {'view': 'global'})
    assert not g.get('organisation')

    # Existing organisation stored
    views.store_organisation(None, {'view': 'org'})
    assert g.organisation['code'] == 'org'
    assert g.organisation['isShared']

    # Non existing organisation
    with pytest.raises(Exception) as exception:
        views.store_organisation(None, {'view': 'not-existing-org'})
        assert str(exception.value) == 'Organisation\'s view is not accessible'

    # Existing organisation without shared view
    organisation.update({'isShared': False})
    with pytest.raises(Exception) as exception:
        views.store_organisation(None, {'view': 'org'})
        assert str(exception.value) == 'Organisation\'s view is not accessible'


def test_index(client):
    """Test frontpage."""
    assert isinstance(views.index(), str)
    assert client.get('/').status_code == 200


def test_search(app, client):
    """Test search."""
    assert isinstance(views.search(), str)
    assert client.get(url_for('documents.search',
                              resource_type='documents')).status_code == 200


def test_detail(app, client, document):
    """Test document detail page."""
    assert client.get(url_for('documents.detail',
                              pid_value=document['pid'])).status_code == 200

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


def test_files_by_type(app):
    """Test filtering files with a specific type."""
    files = [{
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:e73223fe5c54532ebfd3e101cb6527ce',
        'file_id': 'd953c07c-5e7f-4636-bc81-3627f947c494',
        'key': '1_2004ECO001.pdf',
        'label': 'Texte intégral',
        'order': 1,
        'size': 2889638,
        'type': 'file',
        'version_id': '1c9705d3-8a9c-489e-adaf-d7d741b205ba'
    }, {
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:519bd9463e54f681d73861e7e17e2050',
        'file_id': '722264a3-b6d4-459c-a88d-2aca6fe34a0e',
        'key': '1_2004ECO001.txt',
        'size': 160659,
        'type': 'fulltext',
        'version_id': '1194512e-7c99-42e1-b320-a15ccb2ac946'
    }]

    filtered_files = views.files_by_type(files)
    assert len(filtered_files) == 1
    assert filtered_files[0][
        'file_id'] == 'd953c07c-5e7f-4636-bc81-3627f947c494'

    filtered_files = views.files_by_type(files, 'fake')
    assert not filtered_files


def test_file_title():
    """Test getting the caption of a file."""
    assert views.file_title({
        'bucket':
        '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum':
        'md5:e73223fe5c54532ebfd3e101cb6527ce',
        'file_id':
        'd953c07c-5e7f-4636-bc81-3627f947c494',
        'key':
        '1_2004ECO001.pdf',
        'label':
        'Texte intégral',
        'order':
        1,
        'size':
        2889638,
        'type':
        'file',
        'version_id':
        '1c9705d3-8a9c-489e-adaf-d7d741b205ba'
    }) == 'Texte intégral'

    assert views.file_title({
        'bucket':
        '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum':
        'md5:e73223fe5c54532ebfd3e101cb6527ce',
        'file_id':
        'd953c07c-5e7f-4636-bc81-3627f947c494',
        'key':
        '1_2004ECO001.pdf',
        'order':
        1,
        'size':
        2889638,
        'type':
        'file',
        'version_id':
        '1c9705d3-8a9c-489e-adaf-d7d741b205ba'
    }) == '1_2004ECO001.pdf'


def test_thumbnail():
    """Test getting the thumbnail of a file."""
    files = [{
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:e73223fe5c54532ebfd3e101cb6527ce',
        'file_id': 'd953c07c-5e7f-4636-bc81-3627f947c494',
        'key': '1_2004ECO001.pdf',
        'label': 'Texte intégral',
        'order': 1,
        'size': 2889638,
        'type': 'file',
        'version_id': '1c9705d3-8a9c-489e-adaf-d7d741b205ba'
    }, {
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:519bd9463e54f681d73861e7e17e2050',
        'file_id': '722264a3-b6d4-459c-a88d-2aca6fe34a0e',
        'key': '1_2004ECO001.jpg',
        'size': 160659,
        'type': 'thumbnail',
        'version_id': '1194512e-7c99-42e1-b320-a15ccb2ac946'
    }]

    assert views.thumbnail(files[0], files) == {
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:519bd9463e54f681d73861e7e17e2050',
        'file_id': '722264a3-b6d4-459c-a88d-2aca6fe34a0e',
        'key': '1_2004ECO001.jpg',
        'size': 160659,
        'type': 'thumbnail',
        'version_id': '1194512e-7c99-42e1-b320-a15ccb2ac946'
    }

    files = [{
        'bucket': '18126249-6eb7-4fa5-b0b5-f8599e3c2bf0',
        'checksum': 'md5:e73223fe5c54532ebfd3e101cb6527ce',
        'file_id': 'd953c07c-5e7f-4636-bc81-3627f947c494',
        'key': '1_2004ECO001.pdf',
        'label': 'Texte intégral',
        'order': 1,
        'size': 2889638,
        'type': 'file',
        'version_id': '1c9705d3-8a9c-489e-adaf-d7d741b205ba'
    }]

    assert not views.thumbnail(files[0], files)


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
            'pid': 'unisi'
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
        'numberingYear': '2015',
    }) == '2015'


def test_is_file_restricted(app, organisation):
    """Test if a file is restricted by embargo date and/or organisation."""
    g.pop('organisation', None)
    views.store_organisation(None, {'view': 'global'})

    record = {'organisation': {'pid': 'org'}}

    # No restriction and no embargo date
    assert views.is_file_restricted({}, {}) == {
        'date': None,
        'restricted': False
    }

    # Restricted by internal, but IP is allowed
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        assert views.is_file_restricted({'restricted': 'internal'}, {}) == {
            'date': None,
            'restricted': False
        }

    # Restricted by internal, but IP is not allowed
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert views.is_file_restricted({'restricted': 'internal'}, {}) == {
            'date': None,
            'restricted': True
        }

    # Restricted by organisation and organisation is global
    assert views.is_file_restricted({'restricted': 'organisation'},
                                    record) == {
                                        'date': None,
                                        'restricted': True
                                    }

    # Restricted by organisation and current organisation match
    views.store_organisation(None, {'view': 'org'})
    assert views.is_file_restricted({'restricted': 'organisation'},
                                    record) == {
                                        'date': None,
                                        'restricted': False
                                    }

    # Restricted by organisation and record don't have organisation
    assert views.is_file_restricted({'restricted': 'organisation'}, {}) == {
        'date': None,
        'restricted': True
    }

    # Restricted by organisation and organisation don't match
    assert views.is_file_restricted({'restricted': 'organisation'},
                                    {'organisation': {
                                        'pid': 'some-org'
                                    }}) == {
                                        'date': None,
                                        'restricted': True
                                    }

    # Restricted by embargo date only, but embargo date is in the past
    assert views.is_file_restricted({'embargo_date': '2020-01-01'}, {}) == {
        'date': None,
        'restricted': False
    }

    # Restricted by embargo date only and embargo date is in the future
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert views.is_file_restricted({'embargo_date': '2021-01-01'},
                                        {}) == {
                                            'date': datetime.datetime(
                                                2021, 1, 1, 0, 0),
                                            'restricted': True
                                        }

    # Restricted by embargo date and organisation
    g.pop('organisation', None)
    views.store_organisation(None, {'view': 'global'})
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert views.is_file_restricted(
            {
                'embargo_date': '2021-01-01',
                'restricted': 'organisation'
            }, record) == {
                'restricted': True,
                'date': datetime.datetime(2021, 1, 1, 0, 0)
            }

    # Restricted by embargo date but internal IP gives access
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        assert views.is_file_restricted(
            {
                'embargo_date': '2021-01-01',
                'restricted': 'internal'
            }, {}) == {
                'date': None,
                'restricted': False
            }


def test_get_current_organisation_code(app, organisation):
    """Test get current organisation."""
    # No globals and no args
    assert views.get_current_organisation_code() == 'global'

    # Default globals and no args
    views.store_organisation(None, {'view': 'global'})
    assert views.get_current_organisation_code() == 'global'

    # Organisation globals and no args
    views.store_organisation(None, {'view': 'org'})
    assert views.get_current_organisation_code() == 'org'

    # Args is global
    with app.test_request_context() as req:
        req.request.args = {'view': 'global'}
        assert views.get_current_organisation_code() == 'global'

    # Args has organisation view
    with app.test_request_context() as req:
        req.request.args = {'view': 'unisi'}
        assert views.get_current_organisation_code() == 'unisi'


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
