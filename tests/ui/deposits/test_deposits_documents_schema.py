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

"""Test deposits documents schema serializer."""

from sonar.modules.deposits.serializers.schemas.document import \
    DocumentSchema as DepositDocumentSchema


def test_title():
    """Test title."""
    # No title
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'title': [{
            'mainTitle': [{
                'language':
                'ger',
                'value':
                '¿Política exterior o política de cooperación?'
            }],
            'subtitle': [{
                'language':
                'ger',
                'value':
                'una aproximación constructivista al estudio de la política exterior colombiana'
            }],
            'type':
            'bf:Title'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'title':
            '¿Política exterior o política de cooperación?',
            'subtitle':
            'una aproximación constructivista al estudio de la política exterior colombiana'
        }
    }


def test_identified_by():
    """Test identified by."""
    document = {
        'identifiedBy': [{
            'type': 'bf:Doi',
            'value': '10/12345'
        }, {
            'type': 'bf:Isbn',
            'value': '987654'
        }, {
            'type': 'bf:Issn',
            'value': '123456'
        }, {
            'type': 'bf:IssnL',
            'value': '567890'
        }, {
            'type': 'bf:Urn',
            'value': 'urn-value'
        }, {
            'type': 'uri',
            'value': 'https://uri.com'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'identifiedBy': [{
                'type': 'bf:Doi',
                'value': '10/12345'
            }, {
                'type': 'bf:Isbn',
                'value': '987654'
            }, {
                'type': 'bf:Issn',
                'value': '123456'
            }, {
                'type': 'bf:IssnL',
                'value': '567890'
            }, {
                'type': 'bf:Urn',
                'value': 'urn-value'
            }, {
                'type': 'uri',
                'value': 'https://uri.com'
            }]
        }
    }


def test_language():
    """Test language."""
    # No language
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'language': [{
            'type': 'bf:Language',
            'value': 'fre'
        }, {
            'type': 'bf:Language',
            'value': 'ger'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'language': 'fre'
        }
    }


def test_abstracts():
    """Test abstracts."""
    # No abstracts
    assert DepositDocumentSchema().dump({}) == {}

    document = {
        'abstracts': [{
            'language': 'fre',
            'value': 'Abstract FRE'
        }, {
            'language': 'eng',
            'value': 'Abstract ENG'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'abstracts': [{
                'language': 'fre',
                'abstract': 'Abstract FRE'
            }, {
                'language': 'eng',
                'abstract': 'Abstract ENG'
            }]
        }
    }


def test_contribution():
    """Test contribution."""
    # No contribution
    assert DepositDocumentSchema().dump({}) == {}

    document = {
        'contribution': [{
            'agent': {
                'type': 'bf:Person',
                'preferred_name': 'Thilmany, Christian. Herrmann',
                'date_of_birth': '1710',
                'date_of_death': '1767'
            },
            'role': ['cre']
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'contributors': [{
            'name': 'Thilmany, Christian. Herrmann',
            'role': 'cre',
            'date_of_birth': '1710',
            'date_of_death': '1767'
        }]
    }


def test_document_type():
    """Test document type."""
    # No document type
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {'documentType': 'coar:c_2f33'}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'documentType': 'coar:c_2f33'
        }
    }


def test_date():
    """Test date."""
    # No provision activity
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    # No start date
    document = {'provisionActivity': [{}]}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'provisionActivity': [{
            'type': 'bf:Publication',
            'startDate': '2012'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'documentDate': '2012'
        }
    }


def test_content_note():
    """Test content note."""
    document = {'contentNote': ['Note 1', 'Note 2']}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'contentNote': ['Note 1', 'Note 2']
        }
    }


def test_extent():
    """Test extent."""
    document = {'extent': '1 Bd.'}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'extent': '1 Bd.'
        }
    }


def test_dissertation():
    """Test dissertation."""
    document = {
        'dissertation': {
            'degree': 'Diss. Claremont. Complément',
            'grantingInstitution': 'Granting',
            'date': '2019'
        }
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'dissertation': {
                'degree': 'Diss. Claremont. Complément',
                'grantingInstitution': 'Granting',
                'date': '2019'
            }
        }
    }


def test_additional_materials():
    """Test additional materials."""
    document = {'additionalMaterials': '30 pl.'}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'additionalMaterials': '30 pl.'
        }
    }


def test_formats():
    """Test formats."""
    document = {
        'otherMaterialCharacteristics': 'Other material characteristics'
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'otherMaterialCharacteristics': 'Other material characteristics'
        }
    }


def test_other_material_characteristics():
    """Test other material characteristics."""
    document = {'formats': ['24 cm']}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'formats': ['24 cm']
        }
    }


def test_edition_statement():
    """Test edition statement."""
    document = {
        'editionStatement': {
            'editionDesignation': {
                'value': '1st edition'
            },
            'responsibility': {
                'value': 'Resp.'
            }
        }
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'editionStatement': {
                'editionDesignation': {
                    'value': '1st edition'
                },
                'responsibility': {
                    'value': 'Resp.'
                }
            }
        }
    }


def test_publication_place():
    """Test publication place."""
    # No provision activity
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    # No statement
    document = {'provisionActivity': [{}]}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'provisionActivity': [{
            'statement': [{
                'type': 'bf:Place',
                'label': {
                    'value': 'Place 1'
                }
            }, {
                'type': 'bf:Place',
                'label': {
                    'value': 'Place 2'
                }
            }]
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'publicationPlace': 'Place 1'
        }
    }


def test_publisher():
    """Test publisher."""
    # No provision activity
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    # No statement
    document = {'provisionActivity': [{}]}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'provisionActivity': [{
            'statement': [{
                'type': 'bf:Agent',
                'label': {
                    'value': 'Agent 1'
                }
            }, {
                'type': 'bf:Agent',
                'label': {
                    'value': 'Agent 2'
                }
            }]
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'publisher': 'Agent 1'
        }
    }


def test_notes():
    """Test notes."""
    # No note
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {'notes': ['Note 1', 'Note 2']}
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'notes': ['Note 1', 'Note 2']
        }
    }


def test_series():
    """Test series."""
    # No serie
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'series': [{
            'name': 'Serie 1',
            'number': '12'
        }, {
            'name': 'Serie 2'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'series': [{
                'name': 'Serie 1',
                'number': '12'
            }, {
                'name': 'Serie 2'
            }]
        }
    }


def test_part_of():
    """Test part of."""
    # No part of
    document = {}
    assert DepositDocumentSchema().dump(document) == {}

    document = {
        'partOf': [{
            'document': {
                'title':
                'Document title 1',
                'contribution': ['Contributor 1', 'Contributor 2'],
                'identifiedBy': [{
                    'type': 'bf:Issn',
                    'value': 'ISSN'
                }, {
                    'type': 'bf:Isbn',
                    'value': 'ISBN'
                }]
            },
            'numberingVolume': '22',
            'numberingIssue': '4',
            'numberingPages': '485-512',
            'numberingYear': '2004'
        }, {
            'document': {
                'title': 'Document title 2'
            },
            'numberingVolume': '22',
            'numberingIssue': '4',
            'numberingYear': '2004'
        }, {
            'document': {
                'title': 'Document title 3',
            },
            'numberingPages': '243-263'
        }, {
            'document': {
                'title': 'Document title 4'
            },
            'numberingIssue': '16',
            'numberingYear': '2011'
        }]
    }
    assert DepositDocumentSchema().dump(document) == {
        'metadata': {
            'publication': {
                'publishedIn':
                'Document title 1',
                'volume':
                '22',
                'number':
                '4',
                'pages':
                '485-512',
                'year':
                '2004',
                'editors': ['Contributor 1', 'Contributor 2'],
                'identifiedBy': [{
                    'type': 'bf:Issn',
                    'value': 'ISSN'
                }, {
                    'type': 'bf:Isbn',
                    'value': 'ISBN'
                }]
            }
        }
    }
