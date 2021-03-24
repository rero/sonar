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

"""Unpaywall schema."""

from marshmallow import Schema, fields, post_dump


class UnpaywallSchema(Schema):
    """Unpaywall marshmallow schema."""

    files = fields.Method('get_files')
    oa_status = fields.Method('get_oa_status')

    @post_dump
    def remove_empty_values(self, data, **kwargs):
        """Remove empty values before dumping data."""
        return {key: value for key, value in data.items() if value}

    def get_files(self, obj):
        """Get files."""
        if not obj.get('best_oa_location') or not obj['best_oa_location'].get(
                'url_for_pdf'):
            return []

        return [{
            'key': 'fulltext.pdf',
            'url': obj['best_oa_location']['url_for_pdf'],
            'force_external_url': True,
            'label': 'Full-text',
            'type': 'file',
            'order': 0
        }]

    def get_oa_status(self, obj):
        """Get open access status."""
        return obj.get('oa_status')
