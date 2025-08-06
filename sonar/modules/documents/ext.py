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

"""Document extension."""

from invenio_base.signals import app_loaded
from invenio_oaiharvester.signals import oaiharvest_finished

from sonar.modules.documents.receivers import (
    export_json,
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
        oaiharvest_finished.connect(export_json, weak=False)

        # Expand configuration.
        app_loaded.connect(set_boosting_query_fields)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(app.config):
            if k.startswith("SONAR_DOCUMENTS_"):
                app.config.setdefault(k, getattr(config, k))
