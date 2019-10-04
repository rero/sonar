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

"""Document extension."""

from __future__ import absolute_import, print_function

from sonar.modules.permissions import has_admin_access, has_super_admin_access

from . import config


def utility_processor():
    """Dictionary for checking admin access."""
    return dict(has_admin_access=has_admin_access,
                has_super_admin_access=has_super_admin_access)


class Sonar(object):
    """SONAR extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['sonar_app'] = self

        if app.config['SONAR_APP_ENABLE_CORS']:
            from flask_cors import CORS
            CORS(app)

        app.context_processor(utility_processor)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('SONAR_APP_'):
                app.config.setdefault(k, getattr(config, k))
