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

"""Archive ouverte UNIGE schema."""

from marshmallow import fields, pre_dump

from sonar.modules.documents.dojson.archive_ouverte_unige.model import overdo

from .marc21 import Marc21Schema


class ArchiveOuverteUnigeSchema(Marc21Schema):
    """Archive ouverte UNIGE schema."""

    identifiedBy = fields.List(fields.Dict())
    title = fields.List(fields.Dict())

    @pre_dump
    def process(self, obj, **kwargs):
        """All the process is done by overdo."""
        return overdo.do(obj)
