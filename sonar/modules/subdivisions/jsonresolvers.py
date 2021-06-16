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

"""JSON resolvers."""

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from ...config import JSONSCHEMAS_HOST
from .config import Configuration


@jsonresolver.route(Configuration.resolver_url, host=JSONSCHEMAS_HOST)
def json_resolver(pid):
    """Resolve record.

    :param str pid: PID value.
    :return: Record instance.
    :rtype: Record
    """
    resolver = Resolver(pid_type=Configuration.pid_type,
                        object_type='rec',
                        getter=Record.get_record)
    _, record = resolver.resolve(pid)

    if record.get('$schema'):
        del record['$schema']

    return record
