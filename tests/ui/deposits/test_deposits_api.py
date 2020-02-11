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

import json
import os

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.pdf_extractor.utils import format_extracted_data


def test_populate_with_pdf_metadata(app):
    """Test populate deposit with metadata."""
    json_file = os.path.dirname(os.path.abspath(
        __file__)) + '/../pdf_extractor/data/extracted_data.json'

    with open(json_file, 'rb') as file:
        pdf_metadata = format_extracted_data(json.load(file))

        deposit = DepositRecord({})
        deposit.populate_with_pdf_metadata(pdf_metadata)
        assert deposit['metadata']['title'] == 'Calibrated Ice Thickness ' \
            'Estimate for All Glaciers in Austria'

        # With default title
        del pdf_metadata['title']
        deposit.populate_with_pdf_metadata(pdf_metadata, 'Default title')
        assert deposit['metadata']['title'] == 'Default title'


def test_create_document(app, deposit_fixture):
    """Test create document based on it."""
    document = deposit_fixture.create_document()
    assert document['title'][0]['mainTitle'][0][
        'value'] == 'High-harmonic generation in quantum spin systems'
    assert len(document.files) == 4
