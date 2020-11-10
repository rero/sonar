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

"""Test documents utils."""

from flask import g

from sonar.modules.documents import utils
from sonar.modules.documents.views import store_organisation


def test_publication_statement_text():
    """Test publication statement text."""
    # With statement
    assert utils.publication_statement_text({
        'type':
        'bf:Publication',
        'startDate':
        '1990',
        'statement': [{
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
    }) == {
        'default': 'Lausanne : Bulletin officiel du Directoire, 1798-1799'
    }

    # Without statement
    assert utils.publication_statement_text({
        'type': 'bf:Publication',
        'startDate': '1990'
    }) == '1990'

    # Without statement, complete date
    assert utils.publication_statement_text({
        'type': 'bf:Publication',
        'startDate': '1990-12-31'
    }) == '31.12.1990'


def test_get_file_restriction(app, organisation):
    """Test if a file is restricted by embargo date and/or organisation."""
    g.pop('organisation', None)

    store_organisation()

    record = {'organisation': {'pid': 'org'}}

    # No restriction and no embargo date
    assert utils.get_file_restriction({}, {}) == {
        'date': None,
        'restricted': False
    }

    # Restricted by internal, but IP is allowed
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        assert utils.get_file_restriction({'restricted': 'internal'}, {}) == {
            'date': None,
            'restricted': False
        }

    # Restricted by internal, but IP is not allowed
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert utils.get_file_restriction({'restricted': 'internal'}, {}) == {
            'date': None,
            'restricted': True
        }

    # Restricted by organisation and organisation is global
    assert utils.get_file_restriction({'restricted': 'organisation'},
                                      record) == {
                                          'date': None,
                                          'restricted': True
                                      }

    # Restricted by organisation and current organisation match
    with app.test_request_context() as req:
        req.request.view_args['view'] = 'org'
        store_organisation()

    assert utils.get_file_restriction({'restricted': 'organisation'},
                                      record) == {
                                          'date': None,
                                          'restricted': False
                                      }

    # Restricted by organisation and record don't have organisation
    assert utils.get_file_restriction({'restricted': 'organisation'}, {}) == {
        'date': None,
        'restricted': True
    }

    # Restricted by organisation and organisation don't match
    assert utils.get_file_restriction({'restricted': 'organisation'},
                                      {'organisation': {
                                          'pid': 'some-org'
                                      }}) == {
                                          'date': None,
                                          'restricted': True
                                      }

    # Restricted by embargo date only, but embargo date is in the past
    assert utils.get_file_restriction({'embargo_date': '2020-01-01'}, {}) == {
        'date': None,
        'restricted': False
    }

    # Restricted by embargo date only and embargo date is in the future
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert utils.get_file_restriction({'embargo_date': '2021-01-01'},
                                          {}) == {
                                              'date': '01/01/2021',
                                              'restricted': True
                                          }

    # Restricted by embargo date and organisation
    g.pop('organisation', None)
    store_organisation()
    with app.test_request_context(environ_base={'REMOTE_ADDR': '10.1.2.3'}):
        assert utils.get_file_restriction(
            {
                'embargo_date': '2021-01-01',
                'restricted': 'organisation'
            }, record) == {
                'restricted': True,
                'date': '01/01/2021'
            }

    # Restricted by embargo date but internal IP gives access
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        assert utils.get_file_restriction(
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
    assert utils.get_current_organisation_code() == 'global'

    # Default globals and no args
    store_organisation()
    assert utils.get_current_organisation_code() == 'global'

    # Organisation globals and no args
    with app.test_request_context() as req:
        req.request.view_args['view'] = 'org'
        store_organisation()
    assert utils.get_current_organisation_code() == 'org'

    # Args is global
    with app.test_request_context() as req:
        req.request.args = {'view': 'global'}
        assert utils.get_current_organisation_code() == 'global'

    # Args has organisation view
    with app.test_request_context() as req:
        req.request.args = {'view': 'unisi'}
        assert utils.get_current_organisation_code() == 'unisi'


def test_get_file_links(app):
    """Test getting links for a file."""
    document = {'pid': 1, 'external_url': True}
    file = {'key': 'test.pdf', 'restriction': {'restricted': True}}

    # File is restricted
    assert utils.get_file_links(file, document) == {
        'download': None,
        'external': None,
        'preview': None
    }

    # File as an external URL
    file['restriction']['restricted'] = False
    file['external_url'] = 'https://some.url'
    assert utils.get_file_links(file, document) == {
        'download': None,
        'external': 'https://some.url',
        'preview': None
    }

    # File key has no extension, no preview possible
    file['key'] = 'test'
    file['external_url'] = None
    assert utils.get_file_links(file, document) == {
        'download': None,
        'external': None,
        'preview': None
    }

    # Preview not possible
    file['key'] = 'test.unknown'
    file['external_url'] = None
    assert utils.get_file_links(file, document) == {
        'download': '/documents/1/files/test.unknown',
        'external': None,
        'preview': None
    }

    # Preview OK
    file['key'] = 'test.pdf'
    assert utils.get_file_links(file, document) == {
        'download': '/documents/1/files/test.pdf',
        'external': None,
        'preview': '/documents/1/preview/test.pdf'
    }


def test_get_thumbnail():
    """Test get the thumbnail for a file."""
    document = {
        'pid': 1,
        'external_url': True,
        '_files': [{
            'key': 'test.pdf'
        }, {
            'key': 'test-pdf.jpg'
        }]
    }
    file = {'key': 'test.pdf', 'restriction': {'restricted': True}}

    # File is restricted
    assert utils.get_thumbnail(file,
                               document) == 'static/images/restricted.png'

    # Thumbnail is returned
    file['restriction']['restricted'] = False
    assert utils.get_thumbnail(file,
                               document) == '/documents/1/files/test-pdf.jpg'

    # Thumbnail not found
    document['_files'][1]['key'] = 'some-name.jpg'
    assert utils.get_thumbnail(file, document) == 'static/images/no-image.png'
