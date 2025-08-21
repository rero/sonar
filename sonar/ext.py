# Swiss Open Access Repository
# Copyright (C) 2025 RERO
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

import os

import jinja2
from flask import current_app, render_template, request
from flask_bootstrap import Bootstrap4
from flask_security import user_registered
from flask_wiki import Wiki
from invenio_files_rest.signals import file_deleted, file_downloaded, file_uploaded
from invenio_indexer.signals import before_record_index
from werkzeug.datastructures import MIMEAccept

from sonar.filters import (
    favicon,
    get_admin_record_detail_url,
    get_organisation_by_pid,
    get_organisation_by_ref,
    language_value,
    markdown_filter,
    nl2br,
    organisation_platform_name,
)
from sonar.modules.permissions import (
    has_admin_access,
    has_submitter_access,
    has_superuser_access,
)
from sonar.modules.receivers import file_deleted_listener, file_uploaded_listener
from sonar.modules.users.api import current_user_record
from sonar.modules.users.signals import add_full_name, user_registered_handler
from sonar.modules.utils import (
    get_specific_theme,
    get_switch_aai_providers,
    get_view_code,
)
from sonar.modules.validation.views import blueprint as validation_blueprint
from sonar.resources.projects.resource import (
    ProjectsRecordResource,
    ProjectsRecordResourceConfig,
)
from sonar.resources.projects.service import (
    ProjectsRecordService,
    ProjectsRecordServiceConfig,
)
from sonar.signals import file_download_proxy

from . import config_sonar
from .version import __version__


def utility_processor():
    """Dictionary for passing data to templates."""
    return {
        "has_submitter_access": has_submitter_access,
        "has_admin_access": has_admin_access,
        "has_superuser_access": has_superuser_access,
        "ui_version": config_sonar.SONAR_APP_UI_VERSION,
        "aai_providers": get_switch_aai_providers,
        "view_code": get_view_code(),
        "current_user_record": current_user_record,
        "get_specific_theme": get_specific_theme,
    }


class SonarBase:
    """SONAR BASE extension."""

    # Dictionary used to store resources managed by invenio-records-resources
    resources = {}

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

            # Force to load SONAR templates before others
            # it is require for Flask-Security see:
            # https://pythonhosted.org/Flask-Security/customizing.html#emails
            sonar_loader = jinja2.ChoiceLoader([jinja2.PackageLoader("sonar", "templates"), app.jinja_loader])
            app.jinja_loader = sonar_loader
            app.jinja_env.globals["version"] = __version__

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.create_resources()

        app.extensions["sonar"] = self

        # Connect to signal sent when a user is created in Flask-Security.
        user_registered.connect(user_registered_handler, weak=False)

        # Connect to signal sent when a file is uploaded or deleted
        file_uploaded.connect(file_uploaded_listener, weak=False)
        file_downloaded.connect(file_download_proxy, weak=False)
        file_deleted.connect(file_deleted_listener, weak=False)

        # Add user's full name before record index
        before_record_index.connect(add_full_name, weak=False)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config_sonar):
            if k.startswith("SONAR_APP_"):
                app.config.setdefault(k, getattr(config_sonar, k))

        # Set default if not exists.
        if not app.config.get("SONAR_APP_SITEMAP_FOLDER_PATH"):
            app.config.setdefault(
                "SONAR_APP_SITEMAP_FOLDER_PATH",
                os.path.join(app.instance_path, "sitemap"),
            )

        # add keep alive support for angular application
        # NOTE: this will not work for werkzeug> 2.1.2
        # https://werkzeug.palletsprojects.com/en/2.2.x/changes/#version-2-1-2
        if app.config.get("DEBUG"):  # pragma: no cover
            # debug code do not need to be cover by the tests
            from werkzeug.serving import WSGIRequestHandler

            WSGIRequestHandler.protocol_version = "HTTP/1.1"

    def create_resources(self):
        """Create resources."""
        # Initialize the project resource with the corresponding service.
        project_service = ProjectsRecordService(ProjectsRecordServiceConfig())
        projects_resource = ProjectsRecordResource(service=project_service, config=ProjectsRecordResourceConfig)
        self.resources["projects"] = projects_resource

    def get_endpoints(self):
        """Return the list of endpoints available, with the corresponding index.

        :returns: Dictionary of endpoints with corresponding ES index.
        """
        endpoints = {}

        for doc_type, resource in self.resources.items():
            aliases = resource.service.default_config.record_cls.index.get_alias()
            endpoints[doc_type] = next(iter(aliases[next(iter(aliases.keys()))]["aliases"]))

        for doc_type, resource in current_app.config.get("RECORDS_REST_ENDPOINTS").items():
            if resource.get("search_index"):
                endpoints[doc_type] = resource["search_index"]

        return endpoints


class Sonar(SonarBase):
    """SONAR extension."""

    # Dictionary used to store resources managed by invenio-records-resources
    resources = {}

    def init_app(self, app):
        """Flask application initialization."""
        super().init_app(app)
        self.init_views(app)

        if app.config["SONAR_APP_ENABLE_CORS"]:
            from flask_cors import CORS

            CORS(app)

        Bootstrap4(app)
        Wiki(app)

        app.context_processor(utility_processor)

        # add template filters
        app.add_template_filter(nl2br)
        app.add_template_filter(language_value)
        app.add_template_filter(get_admin_record_detail_url)
        app.add_template_filter(favicon)
        app.add_template_filter(organisation_platform_name)
        app.add_template_filter(markdown_filter)
        app.add_template_filter(get_organisation_by_pid)
        app.add_template_filter(get_organisation_by_ref)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config_sonar):
            if k.startswith("SONAR_APP_"):
                app.config.setdefault(k, getattr(config_sonar, k))

        # Set default if not exists.
        if not app.config.get("SONAR_APP_SITEMAP_FOLDER_PATH"):
            app.config.setdefault(
                "SONAR_APP_SITEMAP_FOLDER_PATH",
                os.path.join(app.instance_path, "sitemap"),
            )

        # add keep alive support for angular application
        # NOTE: this will not work for werkzeug> 2.1.2
        # https://werkzeug.palletsprojects.com/en/2.2.x/changes/#version-2-1-2
        if app.config.get("DEBUG"):  # pragma: no cover
            # debug code do not need to be cover by the tests
            from werkzeug.serving import WSGIRequestHandler

            WSGIRequestHandler.protocol_version = "HTTP/1.1"

    def init_views(self, app):
        """Initialize the main flask views."""

        @app.route("/", defaults={"view": app.config.get("SONAR_APP_DEFAULT_ORGANISATION")})
        @app.route("/<org_code:view>")
        def index(view):
            """Homepage."""
            return render_template("sonar/frontpage.html", view=view)


class SonarAPI(SonarBase):
    """SONAR API extension."""

    def __init__(self, app=None):
        """Init for SONAR API extension."""
        super().__init__(app)
        self.register_blueprints(app)

    def register_blueprints(self, app):
        """Register the blueprints."""
        # Register REST endpoint for projects resource.
        app.register_blueprint(self.resources["projects"].as_blueprint())

        # Register REST endpoint for validation module.
        app.register_blueprint(validation_blueprint)

        @app.before_request
        def set_accept_mimetype():
            """Set the accepted mimetype if a `format` args exists.

            This is necessary because accepted formats are not yet implemented
            in flask_resources: https://github.com/inveniosoftware/flask-resources/blob/master/flask_resources/content_negotiation.py#L105
            """
            if request.args.get("format"):
                request.accept_mimetypes = MIMEAccept([(request.args["format"], 1)])
