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

"""SONAR configuration."""

SONAR_APP_API_URL = 'https://localhost:5000/api/'

SONAR_APP_ANGULAR_URL = 'https://localhost:5000/manage/'
"""Link to angular integrated app root."""

SONAR_APP_LANGUAGES_MAP = dict(
    fre='fr',
    ger='de',
    eng='en',
    ita='it',
    spa='sp',
    ara='ar',
    chi='zh',
    lat='la',
    heb='iw',
    jpn='ja',
    por='pt',
    rus='ru'
)

SONAR_APP_PREFERRED_LANGUAGES = ['eng', 'fre', 'ger', 'ita']
"""Order of preferred languages for displaying value in views."""

SONAR_APP_ENABLE_CORS = True

SONAR_APP_DISABLE_PERMISSION_CHECKS = False
"""Disable permission checks during API calls. Useful when API is test from
command line or progams like postman."""

SONAR_APP_UI_VERSION = '0.1.9'
