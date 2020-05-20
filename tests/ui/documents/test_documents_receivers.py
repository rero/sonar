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

"""Test documents recievers."""

from invenio_oaiharvester.tasks import get_records

from sonar.modules.documents.receivers import chunks, \
    populate_fulltext_field, transform_harvested_records


def test_transform_harvested_records(app, bucket_location):
    """Test harvested record transformation."""
    request, records = get_records(
        ['oai:doc.rero.ch:20120503160026-MV'],
        metadata_prefix="marcxml",
        url='http://doc.rero.ch/oai2d',
    )

    transform_harvested_records(None, records, **{'name': 'test', 'max': 1})


def test_populate_fulltext_field(app, db, document, pdf_file):
    """Test add full text to document."""
    with open(pdf_file, 'rb') as file:
        content = file.read()

    # Successful file add
    document.add_file(content, 'test1.pdf', type='file')
    assert document.files['test1.pdf']
    assert document.files['test1.txt']

    db.session.commit()

    json = {}
    populate_fulltext_field(record=document, index='documents', json=json)

    assert len(json['fulltext']) == 1
    assert json['fulltext'][0].startswith('PHYSICAL REVIEW B 99')


def test_chunks():
    """Test chunks."""
    records = chunks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
    records = list(records)
    assert len(records) == 4
    assert records[0] == [1, 2, 3]
    assert records[-1] == [10]
