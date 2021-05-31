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

"""Document extension."""

from __future__ import absolute_import, print_function

import jinja2
import markdown
from flask import current_app, render_template, request
from flask_bootstrap import Bootstrap
from flask_security import user_registered
from flask_wiki import Wiki
from invenio_files_rest.signals import file_deleted, file_uploaded
from invenio_indexer.signals import before_record_index
from werkzeug.datastructures import MIMEAccept

from sonar.modules.collections.receivers import enrich_collection_data
from sonar.modules.permissions import has_admin_access, has_submitter_access, \
    has_superuser_access
from sonar.modules.receivers import file_deleted_listener, \
    file_uploaded_listener
from sonar.modules.users.api import current_user_record
from sonar.modules.users.signals import add_full_name, user_registered_handler
from sonar.modules.utils import get_language_value, get_specific_theme, \
    get_switch_aai_providers, get_view_code
from sonar.resources.projects.resource import \
    RecordResource as ProjectRecordResource
from sonar.resources.projects.service import \
    RecordService as ProjectRecordService

from . import config_sonar
from .route_converters import OrganisationCodeConverter


def utility_processor():
    """Dictionary for passing data to templates."""
    return dict(has_submitter_access=has_submitter_access,
                has_admin_access=has_admin_access,
                has_superuser_access=has_superuser_access,
                ui_version=config_sonar.SONAR_APP_UI_VERSION,
                aai_providers=get_switch_aai_providers,
                view_code=get_view_code(),
                current_user_record=current_user_record,
                get_specific_theme=get_specific_theme)


class Sonar():
    """SONAR extension."""

    # Dictionary used to store resources managed by invenio-records-resources
    resources = {}

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

            # Force to load SONAR templates before others
            # it is require for Flask-Security see:
            # https://pythonhosted.org/Flask-Security/customizing.html#emails
            sonar_loader = jinja2.ChoiceLoader(
                [jinja2.PackageLoader('sonar', 'templates'), app.jinja_loader])
            app.jinja_loader = sonar_loader

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.create_resources()
        self.init_views(app)

        app.extensions['sonar'] = self

        if app.config['SONAR_APP_ENABLE_CORS']:
            from flask_cors import CORS
            CORS(app)

        Bootstrap(app)
        Wiki(app)

        app.context_processor(utility_processor)

        # Connect to signal sent when a user is created in Flask-Security.
        user_registered.connect(user_registered_handler, weak=False)

        # Connect to signal sent when a file is uploaded or deleted
        file_uploaded.connect(file_uploaded_listener, weak=False)
        file_deleted.connect(file_deleted_listener, weak=False)

        # Add user's full name before record index
        before_record_index.connect(add_full_name, weak=False)

        # Enrich collection's data
        before_record_index.connect(enrich_collection_data, weak=False)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config_sonar):
            if k.startswith('SONAR_APP_'):
                app.config.setdefault(k, getattr(config_sonar, k))

    def init_views(self, app):
        """Initialize the main flask views."""
        app.url_map.converters['org_code'] = OrganisationCodeConverter

        @app.route('/<org_code:view>')
        def index(view):
            """Homepage."""
            return render_template('sonar/frontpage.html')

        @app.template_filter()
        def nl2br(string):
            r"""Replace \n to <br>."""
            return string.replace('\n', '<br>')

        @app.template_filter()
        def language_value(values,
                           locale=None,
                           value_field='value',
                           language_field='language'):
            """Get the value of a field corresponding to the current language.

            :params values: List of values with the language.
            :params locale: Two digit locale to find.
            :params value_field: Name of the property containing the value.
            :params language_field: Name of the property containing the language.
            :returns: The value corresponding to the current language.
            """
            return get_language_value(values, locale, value_field,
                                      language_field)

        @app.template_filter()
        def get_admin_record_detail_url(record):
            r"""Return the frontend application URL for a record detail.

            :param record: Record object.
            :returns: Absolute URL to recrod detail.
            :rtype: str
            """
            url = [
                app.config.get('SONAR_APP_ANGULAR_URL')[:-1], 'records',
                record.index_name, 'detail', record.pid.pid_value
            ]
            return '/'.join(url)

        @app.template_filter()
        def markdown_filter(content):
            """Markdown filter.

            :param str content: Content to convert
            :returns: HTML corresponding to markdown
            :rtype: str
            """
            return markdown.markdown(content)

    def create_resources(self):
        """Create resources."""
        # Initialize the project resource with the corresponding service.
        projects_resource = ProjectRecordResource(
            service=ProjectRecordService())
        self.resources['projects'] = projects_resource

    def get_endpoints(self):
        """Return the list of endpoints available, with the corresponding index.

        :returns: Dictionary of endpoints with corresponding ES index.
        """
        endpoints = {}

        for doc_type, resource in self.resources.items():
            aliases = resource.service.default_config.record_cls \
                .index.get_alias()
            endpoints[doc_type] = list(aliases[list(
                aliases.keys())[0]]['aliases'])[0]

        for doc_type, resource in current_app.config.get(
                'RECORDS_REST_ENDPOINTS').items():
            if resource.get('search_index'):
                endpoints[doc_type] = resource['search_index']

        return endpoints


class SonarAPI(Sonar):
    """SONAR API extension."""

    def __init__(self, app=None):
        """Init for SONAR API extension."""
        super().__init__(app)
        self.register_blueprints(app)

    def register_blueprints(self, app):
        """Register the blueprints."""
        # Register REST endpoint for projects resource.
        app.register_blueprint(
            self.resources['projects'].as_blueprint('projects'))

        @app.before_request
        def set_accept_mimetype():
            """Set the accepted mimetype if a `format` args exists.

            This is necessary because accepted formats are not yet implemented
            in flask_resources: https://github.com/inveniosoftware/flask-resources/blob/master/flask_resources/content_negotiation.py#L105
            """
            if request.args.get('format'):
                request.accept_mimetypes = MIMEAccept([(request.args['format'],
                                                        1)])
