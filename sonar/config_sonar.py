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

"""Specific configuration SONAR."""

SONAR_APP_API_URL = 'https://localhost:5000/api/'

SONAR_APP_ANGULAR_URL = 'https://localhost:5000/manage/'
"""Link to angular integrated app root."""

SONAR_APP_LANGUAGES_MAP = dict(fre='fr',
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
                               rus='ru',
                               afr='af')

SONAR_APP_PREFERRED_LANGUAGES = ['eng', 'fre', 'ger', 'ita']
"""Order of preferred languages for displaying value in views."""

SONAR_APP_ENABLE_CORS = True

SONAR_APP_DISABLE_PERMISSION_CHECKS = False
"""Disable permission checks during API calls. Useful when API is test from
command line or progams like postman."""

SONAR_APP_UI_VERSION = '1.0.1'

SONAR_APP_DEFAULT_ORGANISATION = 'global'
"""Default organisation key."""

SONAR_APP_STORAGE_PATH = None
"""File storage location."""

SONAR_APP_EXPORT_SERIALIZERS = {
    'org': ('sonar.modules.organisations.serializers.schemas.export:'
            'ExportSchemaV1'),
    'user': ('sonar.modules.users.serializers.schemas.export:'
             'ExportSchemaV1'),
}

SONAR_APP_FILE_PREVIEW_EXTENSIONS = [
    'jpeg', 'jpg', 'gif', 'png', 'pdf', 'json', 'xml', 'csv', 'zip', 'md'
]
"""List of extensions for which files can be previewed."""

SONAR_APP_WEBDAV_HEG_HOST = 'https://share.rero.ch/HEG'
SONAR_APP_WEBDAV_HEG_USER = None
SONAR_APP_WEBDAV_HEG_PASSWORD = None
"""Connection data to webdav for HEG."""

SONAR_APP_HEG_DATA_DIRECTORY = './data/heg'

SONAR_APP_ORGANISATION_CONFIG = {
    'hepvs': {
        'home_template': 'dedicated/hepvs/home.html',
        'projects': True
    }
}
# Custom resources for organisations

# ARK
# ===

# SONAR_APP_ARK_USER = 'test'
"""Username for the NMA server."""
# SONAR_APP_ARK_PASSWORD = 'test'
"""Password for the NMA server."""
# SONAR_APP_ARK_RESOLVER = 'https://n2t.net'
"""ARK resolver URL."""
# SONAR_APP_ARK_NMA = 'https://www.arketype.ch'
"""ARK Name Mapping Authority: a service provider server."""
# SONAR_APP_ARK_NAAN = '99999'
"""ARK prefix corresponding to an organisation."""
# SONAR_APP_ARK_SCHEME = 'ark:'
"""ARK scheme."""
# SONAR_APP_ARK_SHOULDER = 'ffk3'
"""ARK Shoulder, can be multiple for a given organisation."""
