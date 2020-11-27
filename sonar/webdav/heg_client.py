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

"""HEG webdav client."""

from flask import current_app
from webdav3.client import Client


class HegClient(Client):
    """HEG webdav client."""

    def __init__(self):
        """Constructor of WebDAV client for HEG."""
        options = {
            'webdav_hostname':
            current_app.config.get('SONAR_APP_WEBDAV_HEG_HOST'),
            'webdav_login':
            current_app.config.get('SONAR_APP_WEBDAV_HEG_USER'),
            'webdav_password':
            current_app.config.get('SONAR_APP_WEBDAV_HEG_PASSWORD')
        }

        super(HegClient, self).__init__(options)
