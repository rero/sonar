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

"""DOJSON transformation for Archive ouverte UNIGE."""

from dojson import utils

from sonar.modules.documents.dojson.overdo import Overdo

overdo = Overdo()


@overdo.over('identifiedBy', '001')
@utils.ignore_value
def marc21_to_identified_by_from_001(self, key, value):
    """Get identifier from field 001."""
    identified_by = self.get('identifiedBy', [])

    identified_by.append({
        'type': 'bf:Local',
        'source': 'Archive ouverte UNIGE',
        'value': value
    })

    return identified_by


@overdo.over('title', '^245..')
@utils.for_each_value
@utils.ignore_value
def marc21_to_title_245(self, key, value):
    """Get title."""
    main_title = value.get('a', 'No title found')
    language = value.get('9', 'eng')

    title = {
        'type': 'bf:Title',
        'mainTitle': [{
            'value': main_title,
            'language': language
        }]
    }

    return title


@overdo.over('identifiedBy', '^0247.')
@utils.ignore_value
def marc21_to_identified_by_from_024(self, key, value):
    """Get identifier from field 024."""
    identified_by = self.get('identifiedBy', [])

    if not value.get('a') or not value.get('2') in ['DOI', 'PMID']:
        return None

    if value.get('2') == 'DOI':
        identified_by.append({'type': 'bf:Doi', 'value': value.get('a')})

    if value.get('2') == 'PMID':
        identified_by.append({
            'type': 'bf:Local',
            'source': 'PMID',
            'value': value.get('a')
        })

    return identified_by
