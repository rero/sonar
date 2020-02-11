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

"""Test PDF extractor utils."""

import json
import os

from sonar.modules.pdf_extractor.utils import format_extracted_data


def test_format_extracted_data(app):
    """Test format extracted data."""
    # format_extracted_data({})
    json_file = os.path.dirname(
        os.path.abspath(__file__)) + '/data/extracted_data.json'

    with open(json_file, 'rb') as file:
        # Test standard extraction
        extracted_data = json.load(file)
        formatted_data = format_extracted_data(extracted_data)
        assert 'title' in formatted_data
        assert formatted_data['title'] == 'Calibrated Ice Thickness Estimate' \
            ' for All Glaciers in Austria'
        assert len(formatted_data['authors']) == 2
        assert formatted_data['authors'] == [{
            'affiliation': 'Swiss Institute of Bioinformatics',
            'name': 'Komljenovic Andrea'
        }, {
            'affiliation': 'École Polytechnique Fédérale de Lausanne',
            'name': 'Sleiman Maroun Bou'
        }]

        # Test authors
        extracted_data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'][
            'analytic']['author'] = extracted_data['teiHeader']['fileDesc'][
                'sourceDesc']['biblStruct']['analytic']['author'][0]

        formatted_data = format_extracted_data(extracted_data)
        assert len(formatted_data['authors']) == 1

        # Test languages
        extracted_data['text']['@xml:lang'] = 'de'
        formatted_data = format_extracted_data(extracted_data)
        assert formatted_data['languages'][0] == 'ger'

        # Test imprint
        extracted_data['teiHeader']['fileDesc']['sourceDesc']['biblStruct'][
            'monogr']['imprint']['biblScope'] = extracted_data['teiHeader'][
                'fileDesc']['sourceDesc']['biblStruct']['monogr']['imprint'][
                    'biblScope'][0]
        formatted_data = format_extracted_data(extracted_data)
        assert formatted_data['journal']['name'] == 'Frontiers Media SA'
        assert formatted_data['journal']['volume'] == '7'
