# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HEG webdav client."""

from flask import current_app
from webdav3.client import Client


class HegClient(Client):
    """HEG webdav client."""

    def __init__(self):
        """Constructor of WebDAV client for HEG."""
        options = {
            "webdav_hostname": current_app.config.get("SONAR_APP_WEBDAV_HEG_HOST"),
            "webdav_login": current_app.config.get("SONAR_APP_WEBDAV_HEG_USER"),
            "webdav_password": current_app.config.get("SONAR_APP_WEBDAV_HEG_PASSWORD"),
        }

        super().__init__(options)
