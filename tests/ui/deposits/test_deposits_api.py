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

"""Test API for deposits."""

from invenio_accounts.testutils import login_user_via_view


def test_create_document(app, client, deposit, user):
    """Test create document based on it."""
    login_user_via_view(client, email=user['email'], password='123456')

    document = deposit.create_document()

    assert document['organisation'] == {
        '$ref': 'https://sonar.ch/api/organisations/org'
    }

    assert document['documentType'] == 'coar:c_816b'
    assert document['title'] == [{
        'type':
        'bf:Title',
        'mainTitle': [{
            'language': 'eng',
            'value': 'Title of the document'
        }, {
            'language': 'fre',
            'value': 'Titre du document'
        }],
        'subtitle': [{
            'language': 'eng',
            'value': 'Subtitle of the document'
        }]
    }]
    assert document['language'] == [{'value': 'eng', 'type': 'bf:Language'}]
    assert document['provisionActivity'] == [{
        'type': 'bf:Publication',
        'startDate': '2020-01-01'
    }]
    assert document['partOf'] == [{
        'numberingYear': '2019',
        'numberingPages': '1-12',
        'document': {
            'title': 'Journal',
            'contribution': ['Denson, Edward', 'Worth, James'],
            'publication': {
                'statement': 'Publisher'
            }
        },
        'numberingVolume': '12',
        'numberingIssue': '2'
    }]
    assert document['otherEdition'] == [{
        'document': {
            'electronicLocator': 'https://some.url/document.pdf'
        },
        'publicNote': 'Published version'
    }]
    assert document['specificCollections'] == ['Collection 1', 'Collection 2']
    assert document['classification'] == [{
        'type': 'bf:ClassificationUdc',
        'classificationPortion': '543'
    }]
    assert document['abstracts'] == [{
        'language': 'eng',
        'value': 'Abstract of the document'
    }, {
        'language': 'fre',
        'value': 'Résumé du document'
    }]
    assert document['subjects'] == [{
        'label': {
            'language': 'eng',
            'value': ['Subject 1', 'Subject 2']
        }
    }, {
        'label': {
            'language': 'fre',
            'value': ['Sujet 1', 'Sujet 2']
        }
    }]
    assert document['contribution'] == [{
        'affiliation':
        'University of Bern, Switzerland',
        'agent': {
            'preferred_name': 'Takayoshi, Shintaro',
            'type': 'bf:Person'
        },
        'controlledAffiliation': ['Uni of Bern and Hospital'],
        'role': ['cre']
    }]
    assert document.files['main.pdf']['restricted'] == 'organisation'
    assert document.files['main.pdf']['embargo_date'] == '2021-01-01'
    assert len(document.files) == 6

    # Test without affiliation
    deposit['contributors'][0]['affiliation'] = None
    document = deposit.create_document()

    assert document['contribution'] == [{
        'agent': {
            'preferred_name': 'Takayoshi, Shintaro',
            'type': 'bf:Person'
        },
        'role': ['cre']
    }]
