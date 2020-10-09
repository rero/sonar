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

"""Test Dublic Core marshmallow schema."""

from io import BytesIO

import pytest

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.serializers import dc_v1


@pytest.fixture()
def minimal_document(db, bucket_location, organisation):
    record = DocumentRecord.create(
        {
            'pid':
            '1000',
            'title': [{
                'type':
                'bf:Title',
                'mainTitle': [{
                    'language': 'eng',
                    'value': 'Title of the document'
                }]
            }],
            'organisation': {
                '$ref': 'https://sonar.ch/api/organisations/org'
            }
        },
        dbcommit=True,
        with_bucket=True)
    record.commit()
    db.session.commit()
    return record


@pytest.fixture()
def contributors():
    return [{
        'agent': {
            'preferred_name': 'Creator 1'
        },
        'role': ['cre'],
    }, {
        'agent': {
            'preferred_name': 'Creator 2',
            'number': '123',
            'date': '2019',
            'place': 'Martigny'
        },
        'role': ['cre'],
    }, {
        'agent': {
            'preferred_name': 'Contributor 1'
        },
        'role': ['ctb'],
    }, {
        'agent': {
            'preferred_name': 'Contributor 2',
            'number': '999',
            'date': '2010',
            'place': 'Sion'
        },
        'role': ['ctb'],
    }, {
        'agent': {
            'preferred_name': 'Degree supervisor'
        },
        'role': ['dgs'],
    }, {
        'agent': {
            'preferred_name': 'Printer'
        },
        'role': ['prt'],
    }, {
        'agent': {
            'preferred_name': 'Editor'
        },
        'role': ['edt'],
    }]


def test_contributors(minimal_document, contributors):
    """Test contributors serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['contributors'] == []

    minimal_document.update({'contribution': contributors})
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['contributors'] == [
        'Contributor 1',
        'Contributor 2 (999 : 2010 : Sion)',
        'Degree supervisor',
        'Printer',
        'Editor',
    ]


def test_creators(minimal_document, contributors):
    """Test creators serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['contributors'] == []

    minimal_document.update({'contribution': contributors})
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['creators'] == [
        'Creator 1', 'Creator 2 (123 : 2019 : Martigny)'
    ]


def test_dates(app, minimal_document):
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['dates'] == []

    minimal_document.update({
        'provisionActivity': [{
            'type': 'bf:Agent',
            'startDate': '2019'
        }, {
            'type': 'bf:Publication',
        }, {
            'type': 'bf:Publication',
            'startDate': '2019'
        }, {
            'type': 'bf:Publication',
            'startDate': '2020-01-01'
        }]
    })
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['dates'] == ['2019', '2020-01-01']

    minimal_document.pop('provisionActivity', None)

    minimal_document.files['test.pdf'] = BytesIO(b'File content')
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['dates'] == []

    minimal_document.files['test.pdf']['type'] = 'file'
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['dates'] == []

    with app.test_request_context() as req:
        req.request.args = {'view': 'global'}
        minimal_document.files['test.pdf']['type'] = 'file'
        minimal_document.files['test.pdf']['access'] = 'coar:c_f1cf'
        minimal_document.files['test.pdf']['restricted'] = 'full'
        minimal_document.files['test.pdf']['embargo_date'] = '2022-01-01'
        result = dc_v1.transform_record(minimal_document['pid'],
                                        minimal_document)
        assert result['dates'] == ['info:eu-repo/date/embargoEnd/2022-01-01']


def test_descriptions(minimal_document):
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['descriptions'] == []

    minimal_document['abstracts'] = [{
        'value': 'Description 1'
    }, {
        'value': 'Description 2'
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['descriptions'] == ['Description 1', 'Description 2']


def test_formats(minimal_document):
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['formats'] == []

    minimal_document.files['test.pdf'] = BytesIO(b'File content')
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['formats'] == []

    minimal_document.files['test.pdf'] = BytesIO(b'File content')
    minimal_document.files['test.pdf']['type'] = 'file'
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['formats'] == ['application/pdf']


def test_identifiers(minimal_document):
    """Test identifiers serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['identifiers'] == ['http://localhost/global/documents/1000']


def test_languages(minimal_document):
    """Test languages serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['languages'] == []

    minimal_document['language'] = [{'value': 'eng'}, {'value': 'fre'}]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['languages'] == ['eng', 'fre']


def test_publishers(minimal_document):
    """Test publishers serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['publishers'] == []

    minimal_document['provisionActivity'] = [{
        'type':
        'bf:Manufacture',
        'statement': [{
            'type': 'bf:Agent',
            'label': [{
                'value': 'Publisher'
            }]
        }]
    }, {
        'type': 'bf:Publication'
    }, {
        'type':
        'bf:Publication',
        'statement': [{
            'type': 'bf:Place',
            'label': [{
                'value': 'Place'
            }]
        }]
    }, {
        'type':
        'bf:Publication',
        'statement': [{
            'type': 'bf:Agent',
            'label': [{
                'value': 'Publisher 1'
            }]
        }]
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['publishers'] == ['Publisher 1']


def test_relations(minimal_document):
    """Test relations serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['relations'] == []

    minimal_document['otherEdition'] = [{
        'document': {
            'electronicLocator': 'https://some.url.1'
        }
    }, {
        'document': {
            'electronicLocator': 'https://some.url.2'
        }
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['relations'] == ['https://some.url.1', 'https://some.url.2']

    minimal_document.pop('otherEdition', None)
    minimal_document['identifiedBy'] = [{
        'type': 'bf:Identifier',
        'value': 'ark:/13030/tf5p30086k'
    }, {
        'type': 'bf:Local',
        'value': '10.1186'
    }, {
        'type': 'bf:Doi',
        'value': '09.1186'
    }, {
        'type': 'bf:Doi',
        'value': '10.1186/2041-1480-3-9'
    }, {
        'type': 'bf:Isbn',
        'value': '123456'
    }, {
        'type': 'bf:Issn',
        'value': '987654321'
    }, {
        'type': 'bf:Local',
        'source': 'some pmid',
        'value': '1111111'
    }, {
        'type': 'bf:Local',
        'source': 'PMID',
        'value': '2222222'
    }, {
        'type': 'bf:Urn',
        'value': '1.2.3.4'
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['relations'] == [
        'info:eu-repo/semantics/altIdentifier/ark/13030/tf5p30086k',
        'info:eu-repo/semantics/altIdentifier/doi/10.1186/2041-1480-3-9',
        'info:eu-repo/semantics/altIdentifier/isbn/123456',
        'info:eu-repo/semantics/altIdentifier/issn/987654321',
        'info:eu-repo/semantics/altIdentifier/pmid/1111111',
        'info:eu-repo/semantics/altIdentifier/pmid/2222222',
        'info:eu-repo/semantics/altIdentifier/urn/1.2.3.4'
    ]


def test_rights(app, minimal_document):
    """Test rights serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['rights'] == []

    minimal_document['usageAndAccessPolicy'] = {'license': 'CC BY-NC-SA'}
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['rights'] == ['CC BY-NC-SA']

    minimal_document['usageAndAccessPolicy'] = {
        'license': 'Other OA / license undefined',
        'label': 'Custom license'
    }
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['rights'] == ['Other OA / license undefined, Custom license']

    minimal_document.pop('usageAndAccessPolicy', None)
    with app.test_request_context() as req:
        req.request.args = {'view': 'global'}

        minimal_document.files['test.pdf'] = BytesIO(b'File content')
        minimal_document.files['test.pdf']['type'] = 'file'
        result = dc_v1.transform_record(minimal_document['pid'],
                                        minimal_document)
        assert result['rights'] == ['info:eu-repo/semantics/openAccess']

        minimal_document.files['test.pdf']['access'] = 'coar:c_16ec'
        minimal_document.files['test.pdf']['restricted'] = 'full'
        result = dc_v1.transform_record(minimal_document['pid'],
                                        minimal_document)
        assert result['rights'] == ['info:eu-repo/semantics/restrictedAccess']

        minimal_document.files['test.pdf']['access'] = 'coar:c_f1cf'
        minimal_document.files['test.pdf']['embargo_date'] = '2022-01-01'
        result = dc_v1.transform_record(minimal_document['pid'],
                                        minimal_document)
        assert result['rights'] == ['info:eu-repo/semantics/embargoedAccess']


def test_sources(minimal_document):
    """Test sources serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['sources'] == []

    minimal_document['partOf'] = [{
        'document': {
            'title': 'Document 1'
        },
        'numberingYear': '2020'
    }, {
        'document': {
            'title': 'Document 2'
        },
        'numberingYear': '2020',
        'numberingVolume': '6',
        'numberingPages': '135-139',
        'numberingIssue': '12'
    }, {
        'document': {
            'title': 'Document 3'
        },
        'numberingYear': '2019',
        'numberingPages': '135-139',
        'numberingIssue': '12'
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['sources'] == [
        'Document 1, 2020',
        'Document 2, 2020, vol. 6, no. 12, p. 135-139',
        'Document 3, 2019',
    ]


def test_subjects(minimal_document):
    """Test subjects serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['subjects'] == []

    minimal_document['subjects'] = [{
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
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['subjects'] == [
        'Subject 1', 'Subject 2', 'Sujet 1', 'Sujet 2'
    ]

    minimal_document.pop('subjects', None)
    minimal_document['classification'] = [{
        'type': 'bf:ClassificationUdc',
        'classificationPortion': '54'
    }, {
        'type': 'bf:ClassificationDdc',
        'classificationPortion': 'Portion'
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['subjects'] == [
        'info:eu-repo/classification/udc/54',
        'info:eu-repo/classification/ddc/Portion'
    ]


def test_titles(minimal_document):
    """Test titles serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['titles'] == ['Title of the document']

    minimal_document['title'] = [{
        'mainTitle': [{
            'language': 'eng',
            'value': 'Title 1'
        }]
    }, {
        'mainTitle': [{
            'language': 'eng',
            'value': 'Title 2'
        }]
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['titles'] == ['Title 1']

    minimal_document['title'] = [{
        'mainTitle': [{
            'language': 'eng',
            'value': 'Title 1'
        }],
        'subtitle': [{
            'language': 'eng',
            'value': 'Subtitle 1'
        }]
    }]
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['titles'] == ['Title 1 : Subtitle 1']


def test_types(minimal_document):
    """Test types serialization."""
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['types'] == []

    minimal_document['documentType'] = 'coar:c_2f33'
    result = dc_v1.transform_record(minimal_document['pid'], minimal_document)
    assert result['types'] == ['http://purl.org/coar/resource_type/c_2f33']
