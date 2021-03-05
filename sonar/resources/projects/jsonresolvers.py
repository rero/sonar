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

"""Project resolver."""

import jsonresolver

from sonar.proxies import sonar


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route('/api/projects/<pid>', host='sonar.ch')
def project_resolver(pid):
    """Resolve referenced project.

    This resolver is kept for compatibility reason with old resource
    management.
    """
    record = sonar.service('projects').record_cls.pid.resolve(pid)

    data = {'pid': record['id'], 'name': record['metadata']['name']}

    if record['metadata'].get('investigators'):
        data['investigators'] = record['metadata']['investigators']

    return data
