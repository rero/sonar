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

"""Test documents recievers."""

import random

from sonar.modules.documents.dumpers import IndexerDumper


def test_document_indexer_dumper(document, pdf_file):
    """Test add full text to document."""
    with open(pdf_file, 'rb') as file:
        content = file.read()

    # Successful file add
    document.add_file(content, 'test1.pdf', type='file')
    assert document.files['test1.pdf']
    assert document.files['test1-pdf.txt']

    data = document.dumps(IndexerDumper())

    assert len(data['fulltext']) == 1
    assert 'PHYSICAL REVIEW B 99' in data['fulltext'][0]
    assert data['_updated']
    assert 'ips' in data['organisation'][0]
    assert 'isOpenAccess' in data
    assert 'identifiers' in data

def test_document_indexer_dumper_identifiers(document):
    """Test the additional identifiers produced by the dumper."""

    types = [
        "bf:AudioIssueNumber",
        "bf:Doi",
        "bf:Ean",
        "bf:Gtin14Number",
        "ark",
        "bf:Identifier",
        "bf:Isan",
        "bf:Isbn",
        "bf:Ismn",
        "bf:Isrc",
        "bf:Issn",
        "bf:Local",
        "bf:IssnL",
        "bf:MatrixNumber",
        "bf:MusicDistributorNumber",
        "bf:MusicPlate",
        "bf:MusicPublisherNumber",
        "bf:PublisherNumber",
        "bf:Upc",
        "bf:Urn",
        "bf:VideoRecordingNumber",
        "uri",
        "bf:ReportNumber",
        "bf:Strn"
    ]
    n = 0
    document['identifiedBy'] = []
    res = {}
    for t in types:
        key = t.split(':')[-1].lower()
        for _ in range(random.randint(1,5)):
            value = f'value{n}'
            document['identifiedBy'].append(dict(type=t, value=value))
            res.setdefault(key, []).append(value)
            n += 1

    data = document.dumps(IndexerDumper())
    assert data['identifiers'] == res
