# -*- coding: utf-8 -*-
#
# RERO ILS
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""JS/CSS bundles for RERO ILS theme."""

from __future__ import absolute_import

from invenio_assets import NpmBundle

admin_ui_js = NpmBundle(
    'node_modules/@rero/sonar-ui/dist/admin/runtime.js',
    'node_modules/@rero/sonar-ui/dist/admin/polyfills.js',
    'node_modules/@rero/sonar-ui/dist/admin/main.js',
    output='admin_ui.%(version)s.js',
    npm={
        '@rero/sonar-ui': '~0.0.1'
    }
)

admin_ui_css = NpmBundle(
    'node_modules/@rero/sonar-ui/dist/admin/styles.css',
    output='admin_ui.%(version)s.css',
    npm={
        '@rero/sonar-ui': '~0.0.1'
    }
)
