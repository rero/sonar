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

"""Document resolver."""

from __future__ import absolute_import, print_function

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route('/api/documents/<pid>', host='sonar.ch')
def document_resolver(pid):
    """Resolve referenced document."""
    resolver = Resolver(pid_type='doc', object_type="rec",
                        getter=Record.get_record)
    _, record = resolver.resolve(pid)

    if record.get('$schema'):
        del record['$schema']

    return record
