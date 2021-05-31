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

"""Signal receivers for collections."""


def enrich_collection_data(sender=None,
                           record=None,
                           json=None,
                           index=None,
                           **kwargs):
    """Receive a signal before record is indexed, to enrich the data.

    :param sender: Sender of the signal.
    :param Record record: Record to index.
    :param dict json: JSON that will be indexed.
    :param str index: Name of the index in which record will be sent.
    """
    if not index.startswith('collections'):
        return

    def _build_path(parent, path):
        """Recursive call to build the path from parent node to leaf.

        :param parent: Parent item.
        :param path: List of PIDs.
        """
        if not parent:
            return

        path.insert(0, parent['pid'])
        _build_path(parent.get('parent'), path)

    # Make the pass
    path = [json['pid']]
    _build_path(json.get('parent'), path)
    path.insert(0, '')
    json['path'] = '/'.join(path)
