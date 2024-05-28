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

"""Test documents utils."""

from sonar.modules.documents import utils


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
        },
        {
            "label": [{
                "value": "1900-1999"
            }],
            "type": "Date"
        }]
    }) == {
        'default': 'Lausanne : Bulletin officiel du Directoire, 1798-1799, 1900-1999'
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


def test_get_file_restriction(app, organisation, admin, monkeypatch,
                              embargo_date):
    """Test if a file is restricted by embargo date and/or organisation."""
    # No view arg, file is allowed
    assert utils.get_file_restriction({}, [organisation]) == {
        'restricted': False,
        'date': None
    }

    with app.test_request_context(
            environ_base={'REMOTE_ADDR': '127.0.0.1'}) as req:
        req.request.args = {'view': 'global'}

        # No access property, file is allowed
        assert utils.get_file_restriction({}, [organisation]) == {
            'date': None,
            'restricted': False
        }

        # No access property, file is allowed
        assert utils.get_file_restriction({}, [organisation]) == {
            'date': None,
            'restricted': False
        }

        # Access property is open access, file is allowed
        assert utils.get_file_restriction({'access': 'coar:c_abf2'},
                                          [organisation]) == {
                                              'date': None,
                                              'restricted': False
                                          }

        # Embargo access, but no date specified, file is allowed
        assert utils.get_file_restriction({'access': 'coar:c_f1cf'},
                                          [organisation]) == {
                                              'date': None,
                                              'restricted': False
                                          }

        # Embargo access, but date is invalid, file is allowed
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'embargo_date': 'wrong'
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }

        # Embargo access, but date is in the past, file is allowed
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'embargo_date': '2010-01-01'
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }

        # Embargo access, restriction is not defined, no access
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is full, no access
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': False,
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, no user logged
        # and IP is not white listed.
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, []) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, user logged but
        # organisation does not exist in record --> file is locked
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, []) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, user logged but
        # organisations are not corresponding --> file is locked
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'another-org'})
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, user logged and
        # organisations are matching --> file is accessible
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'org'})
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }

        # Embargo access, restriction is outside organisation, user logged and
        # IP is not white listed --> file is locked
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'another-org'})
        organisation['allowedIps'] = ''
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': embargo_date.strftime('%d/%m/%Y'),
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, user logged and
        # IP is white listed --> file is accessible
        organisation['allowedIps'] = '127.0.0.1'
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_f1cf',
                'restricted_outside_organisation': True,
                'embargo_date': embargo_date.isoformat()
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }

        # Reset allowed IPs
        organisation['allowedIps'] = ''

        # Restricted access, restriction is not defined, no access
        assert utils.get_file_restriction({
            'access': 'coar:c_16ec',
        }, [organisation]) == {
            'date': None,
            'restricted': True
        }

        # Restricted access, restriction is full, no access
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': False,
            }, [organisation]) == {
                'date': None,
                'restricted': True
            }

        # Restricted access, restriction is outside organisation, no user
        # logged and IP is not white listed.
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, []) == {
                'date': None,
                'restricted': True
            }

        # Restricted access, restriction is outside organisation, user logged
        # but organisation does not exist in record --> file is locked
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, []) == {
                'date': None,
                'restricted': True
            }

        # Restricted access, restriction is outside organisation, user logged
        # but organisations are not corresponding --> file is locked
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'another-org'})
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, [organisation]) == {
                'date': None,
                'restricted': True
            }

        # Restricted access, restriction is outside organisation, user logged
        # and organisations are matching --> file is accessible
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'org'})
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }

        # Restricted access, restriction is outside organisation, user logged
        # and IP is not white listed --> file is locked
        monkeypatch.setattr(
            'sonar.modules.documents.utils.current_organisation',
            {'pid': 'another-org'})
        organisation['allowedIps'] = ''
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, [organisation]) == {
                'date': None,
                'restricted': True
            }

        # Embargo access, restriction is outside organisation, user logged and
        # IP is white listed --> file is accessible
        organisation['allowedIps'] = '127.0.0.1'
        assert utils.get_file_restriction(
            {
                'access': 'coar:c_16ec',
                'restricted_outside_organisation': True,
            }, [organisation]) == {
                'date': None,
                'restricted': False
            }


def test_get_file_links(app):
    """Test getting links for a file."""
    document = {'pid': 1, 'external_url': True}
    file = {
        'key': 'test.pdf',
        'restriction': {'restricted': True},
        'mimetype': 'application/pdf'
    }

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
    del file['mimetype']
    assert utils.get_file_links(file, document) == {
        'download': None,
        'external': None,
        'preview': None
    }

    # Preview not possible
    file['key'] = 'test.tiff'
    file['external_url'] = None
    file['mimetype'] = 'image/tiff'
    assert utils.get_file_links(file, document) == {
        'download': '/documents/1/files/test.tiff',
        'external': None,
        'preview': None
    }

    # File key has no extension, no preview possible
    file['key'] = 'test.foo'
    file['external_url'] = None
    file['mimetype'] = 'application/octet-stream'
    assert utils.get_file_links(file, document) == {
        'download': f'/documents/1/files/test.foo',
        'external': None,
        'preview': None
    }

    # Preview OK
    mimetypes = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/octet-stream',
        'image/gif',
        'text/csv',
        'application/json',
        'application/xml'
    ]
    for mimetype in mimetypes:
        ext = mimetype.split('/')[1]
        if ext == 'octet-stream':
            ext = 'md'
        file['key'] = f'test.{ext}'
        file['mimetype'] = mimetype
        assert utils.get_file_links(file, document) == {
            'download': f'/documents/1/files/test.{ext}',
            'external': None,
            'preview': f'/documents/1/preview/test.{ext}'
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
