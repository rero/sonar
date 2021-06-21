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

"""JS/CSS Webpack bundles for theme."""

from __future__ import absolute_import, print_function

from flask_webpackext import WebpackBundle

from sonar.config_sonar import SONAR_APP_UI_VERSION

theme = WebpackBundle(__name__,
                      'assets',
                      entry={
                          'global-theme': './scss/global/theme.scss',
                          'usi-theme': './scss/usi/theme.scss',
                          'hepvs-theme': './scss/hepvs/theme.scss',
                          'vge-theme': './scss/vge/theme.scss',
                          'hepbejune-theme': './scss/hepbejune/theme.scss',
                          'preview': './scss/preview.scss',
                      },
                      dependencies={
                          'bootstrap': '^4.3',
                          'popper.js': '^1.12',
                          'font-awesome': '^4.0',
                          'ngx-toastr': '^10.2.0',
                          '@rero/sonar-ui': SONAR_APP_UI_VERSION
                      })
