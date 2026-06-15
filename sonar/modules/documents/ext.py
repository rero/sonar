# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Document extension."""

from invenio_base.signals import app_loaded
from invenio_oaiharvester.signals import oaiharvest_finished

from sonar.modules.documents.receivers import (
    set_boosting_query_fields,
    transform_harvested_records,
)

from . import config


class Documents:
    """SONAR documents extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["sonar_documents"] = self

        # Connect to oaiharvester signal
        oaiharvest_finished.connect(transform_harvested_records, weak=False)
        # disabled HEG export for now
        # oaiharvest_finished.connect(export_json, weak=False)

        # Expand configuration.
        app_loaded.connect(set_boosting_query_fields)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(app.config):
            if k.startswith("SONAR_DOCUMENTS_"):
                app.config.setdefault(k, getattr(config, k))
