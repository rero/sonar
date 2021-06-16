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

"""Default configuration for Swiss Open Access Repository.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

import os
from datetime import timedelta

from invenio_oauthclient.contrib import orcid
from invenio_records_rest.facets import range_filter
from invenio_stats.processors import EventsIndexer

from sonar.modules.collections.config import \
    Configuration as CollectionConfiguration
from sonar.modules.deposits.api import DepositRecord, DepositSearch
from sonar.modules.deposits.permissions import DepositPermission
from sonar.modules.documents.api import DocumentRecord, DocumentSearch
from sonar.modules.documents.permissions import DocumentPermission
from sonar.modules.organisations.api import OrganisationRecord, \
    OrganisationSearch
from sonar.modules.organisations.permissions import OrganisationPermission
from sonar.modules.permissions import record_permission_factory, \
    wiki_edit_permission
from sonar.modules.query import and_term_filter, missing_field_filter
from sonar.modules.subdivisions.config import \
    Configuration as SubdivisionConfiguration
from sonar.modules.users.api import UserRecord, UserSearch
from sonar.modules.users.permissions import UserPermission
from sonar.modules.utils import get_current_language


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Application default theme, used in several modules (previewer, admin, ...)
APP_THEME = ['bootstrap3']

# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/3'
#: Disable rate limit to avoid 429 http error
RATELIMIT_ENABLED = False

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [('fr', _('French')), ('de', _('German')),
                  ('it', _('Italian'))]

# Base templates
# ==============
#: Global base template.
BASE_TEMPLATE = 'sonar/page.html'
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = 'sonar/page_cover.html'
#: Settings base template.
SETTINGS_TEMPLATE = 'sonar/page_settings.html'

# Logging
# =======
LOGGING_SENTRY_LEVEL = "ERROR"
LOGGING_SENTRY_CELERY = True
LOGGING_FS_LEVEL = "WARNING"
LOGGING_FS_LOGFILE = '{instance_path}/app.log'

# Theme configuration
# ===================
#: Site name
THEME_SITENAME = _('Swiss Open Access Repository')
#: Use default frontpage.
THEME_FRONTPAGE = True
#: Frontpage title.
THEME_FRONTPAGE_TITLE = _('Swiss Open Access Repository')
#: Frontpage template.
THEME_FRONTPAGE_TEMPLATE = 'sonar/frontpage.html'
#: Theme logo
THEME_LOGO = 'images/global-logo.svg'

THEME_ERROR_TEMPLATE = 'sonar/page_error.html'
# Analytics tracking code
THEME_TRACKINGCODE_TEMPLATE = 'sonar/trackingcode.html'

# Email configuration
# ===================
#: Email address for support.
SUPPORT_EMAIL = "software@rero.ch"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True

# Assets
# ======
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = 'flask_collect.storage.file'

# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _(
    'Welcome to SONAR, the Swiss Open Access Repository!')
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = 'redis://localhost:6379/1'
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True
# make security blueprints available to the REST API
ACCOUNTS_REGISTER_BLUEPRINT = True

# User profiles
# =============
USERPROFILES = False

# Celery configuration
# ====================

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'
#: URL of backend for result storage (default is Redis).
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
#: Scheduled tasks configuration (aka cronjobs).
CELERY_BEAT_SCHEDULE = {
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'accounts': {
        'task': 'invenio_accounts.tasks.clean_session_table',
        'schedule': timedelta(minutes=60),
    },
    # Stats
    'stats-process-events': {
        'task': 'invenio_stats.tasks.process_events',
        'schedule': timedelta(minutes=30),
        'args': [('record-view', 'file-download')],
    }
}
CELERY_BROKER_HEARTBEAT = 0
#: Disable sending heartbeat events

# Indexer
# ========
#: Bulk index request timeout
INDEXER_BULK_REQUEST_TIMEOUT = 60

# Database
# ========
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = \
    'postgresql+psycopg2://sonar:sonar@localhost/sonar'

# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = 'sonar.ch'

# Flask configuration
# ===================
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'CHANGE_ME'
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True
#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['sonar.ch', 'localhost', '127.0.0.1']

APP_DEFAULT_SECURE_HEADERS = {
    'force_https': True,
    'force_https_permanent': False,
    'force_file_save': False,
    'frame_options': 'sameorigin',
    'frame_options_allow_from': None,
    'strict_transport_security': True,
    'strict_transport_security_preload': False,
    'strict_transport_security_max_age': 31556926,  # One year in seconds
    'strict_transport_security_include_subdomains': True,
    'content_security_policy': {
        'default-src': ["'self'", 'https://www.google-analytics.com'],
        'object-src': ["'none'"],
        'script-src': [
            "'self'", "'unsafe-inline'", "'unsafe-eval'",
            'https://code.jquery.com', 'https://cdnjs.cloudflare.com',
            'https://stackpath.bootstrapcdn.com',
            'https://www.googletagmanager.com',
            'https://www.google-analytics.com'
        ],
        'style-src': [
            "'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com'
        ],
        'font-src': [
            "'self'", "data:", "blob:", "'unsafe-inline'",
            'https://cdnjs.cloudflare.com', 'https://fonts.gstatic.com'
        ],
        'img-src':
        ["'self'", "data:", "blob:", 'https://www.google-analytics.com']
    },
    'content_security_policy_report_uri': None,
    'content_security_policy_report_only': False,
    'session_cookie_secure': True,
    'session_cookie_http_only': True
}
"""Talisman default Secure Headers configuration."""

# OAI-PMH
# =======
OAISERVER_ID_PREFIX = 'oai:sonar.ch:'

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

PIDSTORE_RECID_FIELD = 'pid'

SECURITY_LOGIN_USER_TEMPLATE = 'sonar/accounts/login.html'
SECURITY_FORGOT_PASSWORD_TEMPLATE = 'sonar/accounts/forgot_password.html'
SECURITY_RESET_PASSWORD_TEMPLATE = 'sonar/accounts/reset_password.html'
SECURITY_REGISTER_USER_TEMPLATE = 'sonar/accounts/signup.html'

RECORDS_UI_ENDPOINTS = {
    'doc': {
        'pid_type': 'doc',
        'route': '/<org_code:view>/documents/<pid_value>',
        'view_imp': 'sonar.modules.documents.views:detail',
        'record_class': 'sonar.modules.documents.api:DocumentRecord',
        'template': 'documents/record.html'
    },
    'doc_previewer': {
        'pid_type': 'doc',
        'route': '/documents/<pid_value>/preview/<filename>',
        'view_imp': 'invenio_previewer.views:preview',
        'record_class': 'sonar.modules.documents.api:DocumentRecord'
    },
    'doc_files': {
        'pid_type': 'doc',
        'route': '/documents/<pid_value>/files/<filename>',
        'view_imp': 'invenio_records_files.utils:file_download_ui',
        'record_class': 'invenio_records_files.api:Record'
    },
    'depo_previewer': {
        'pid_type': 'depo',
        'route': '/deposits/<pid_value>/preview/<filename>',
        'view_imp': 'invenio_previewer.views:preview',
        'record_class': 'sonar.modules.deposits.api:DepositRecord'
    },
    'depo_files': {
        'pid_type': 'depo',
        'route': '/deposits/<pid_value>/files/<filename>',
        'view_imp': 'invenio_records_files.utils:file_download_ui',
        'record_class': 'invenio_records_files.api:Record'
    },
    'org_previewer': {
        'pid_type': 'org',
        'route': '/organisations/<pid_value>/preview/<filename>',
        'view_imp': 'invenio_previewer.views:preview',
        'record_class': 'sonar.modules.organisations.api:OrganisationRecord'
    },
    'org_files': {
        'pid_type': 'org',
        'route': '/organisations/<pid_value>/files/<filename>',
        'view_imp': 'invenio_records_files.utils:file_download_ui',
        'record_class': 'invenio_records_files.api:Record'
    },
    'proj': {
        'pid_type': 'proj',
        'route': '/<org_code:view>/projects/<pid_value>',
        'view_imp': 'sonar.resources.projects.views:detail',
        'record_class': 'sonar.resources.projects.api:Record',
        'template': 'sonar/projects/detail.html'
    },
    'coll': {
        'pid_type': 'coll',
        'route': '/<org_code:view>/collections/<pid_value>',
        'view_imp': 'sonar.modules.collections.views:detail',
        'record_class': 'sonar.modules.collections.api:Record',
        'template': 'sonar/collections/detail.html'
    },
    'coll_previewer': {
        'pid_type': 'coll',
        'route': '/collections/<pid_value>/preview/<filename>',
        'view_imp': 'invenio_previewer.views:preview',
        'record_class': 'sonar.modules.collections.api:Record'
    },
    'coll_files': {
        'pid_type': 'coll',
        'route': '/collections/<pid_value>/files/<filename>',
        'view_imp': 'invenio_records_files.utils:file_download_ui',
        'record_class': 'invenio_records_files.api:Record'
    },
}
"""Records UI for sonar."""

RECORDS_REST_ENDPOINTS = {
    'doc':
    dict(
        pid_type='doc',
        pid_minter='document_id',
        pid_fetcher='document_id',
        default_endpoint_prefix=True,
        record_class=DocumentRecord,
        search_class=DocumentSearch,
        indexer_class='sonar.modules.documents.api:DocumentIndexer',
        search_index='documents',
        search_type=None,
        record_serializers={
            'application/json': ('sonar.modules.documents.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('sonar.modules.documents.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('sonar.modules.documents.loaders'
                                 ':json_v1'),
        },
        list_route='/documents/',
        item_route='/documents/<pid(doc, record_class="sonar.modules.'
        'documents.api:DocumentRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='sonar.modules.documents.query:search_factory',
        create_permission_factory_imp=lambda record: record_permission_factory(
            action='create', cls=DocumentPermission),
        read_permission_factory_imp=lambda record: record_permission_factory(
            action='read', record=record, cls=DocumentPermission),
        update_permission_factory_imp=lambda record: record_permission_factory(
            action='update', record=record, cls=DocumentPermission),
        delete_permission_factory_imp=lambda record: record_permission_factory(
            action='delete', record=record, cls=DocumentPermission),
        list_permission_factory_imp=lambda record: record_permission_factory(
            action='list', record=record, cls=DocumentPermission)),
    'org':
    dict(
        pid_type='org',
        pid_minter='organisation_id',
        pid_fetcher='organisation_id',
        default_endpoint_prefix=True,
        record_class=OrganisationRecord,
        search_class=OrganisationSearch,
        indexer_class='sonar.modules.organisations.api:OrganisationIndexer',
        search_index='organisations',
        search_type=None,
        record_serializers={
            'application/json': ('sonar.modules.organisations.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('sonar.modules.organisations.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('sonar.modules.organisations.loaders'
                                 ':json_v1'),
        },
        list_route='/organisations/',
        item_route='/organisations/<pid(org, record_class="sonar.modules.'
        'organisations.api:OrganisationRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='sonar.modules.organisations.query:search_factory',
        create_permission_factory_imp=lambda record: record_permission_factory(
            action='create', cls=OrganisationPermission),
        read_permission_factory_imp=lambda record: record_permission_factory(
            action='read', record=record, cls=OrganisationPermission),
        update_permission_factory_imp=lambda record: record_permission_factory(
            action='update', record=record, cls=OrganisationPermission),
        delete_permission_factory_imp=lambda record: record_permission_factory(
            action='delete', record=record, cls=OrganisationPermission),
        list_permission_factory_imp=lambda record: record_permission_factory(
            action='list', record=record, cls=OrganisationPermission)),
    'user':
    dict(
        pid_type='user',
        pid_minter='user_id',
        pid_fetcher='user_id',
        default_endpoint_prefix=True,
        record_class=UserRecord,
        search_class=UserSearch,
        indexer_class='sonar.modules.users.api:UserIndexer',
        search_index='users',
        search_type=None,
        record_serializers={
            'application/json': ('sonar.modules.users.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('sonar.modules.users.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('sonar.modules.users.loaders'
                                 ':json_v1'),
        },
        list_route='/users/',
        item_route='/users/<pid(user, record_class="sonar.modules.'
        'users.api:UserRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='sonar.modules.users.query:search_factory',
        create_permission_factory_imp=lambda record: record_permission_factory(
            action='create', cls=UserPermission),
        read_permission_factory_imp=lambda record: record_permission_factory(
            action='read', record=record, cls=UserPermission),
        update_permission_factory_imp=lambda record: record_permission_factory(
            action='update', record=record, cls=UserPermission),
        delete_permission_factory_imp=lambda record: record_permission_factory(
            action='delete', record=record, cls=UserPermission),
        list_permission_factory_imp=lambda record: record_permission_factory(
            action='list', record=record, cls=UserPermission)),
    'depo':
    dict(
        pid_type='depo',
        pid_minter='deposit_id',
        pid_fetcher='deposit_id',
        default_endpoint_prefix=True,
        record_class=DepositRecord,
        search_class=DepositSearch,
        indexer_class='sonar.modules.deposits.api:DepositIndexer',
        search_index='deposits',
        search_type=None,
        record_serializers={
            'application/json': ('sonar.modules.deposits.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('sonar.modules.deposits.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('sonar.modules.deposits.loaders'
                                 ':json_v1'),
        },
        list_route='/deposits/',
        item_route='/deposits/<pid(depo, record_class="sonar.modules.deposits'
        '.api:DepositRecord"):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        search_factory_imp='sonar.modules.deposits.query:search_factory',
        create_permission_factory_imp=lambda record: record_permission_factory(
            action='create', cls=DepositPermission),
        read_permission_factory_imp=lambda record: record_permission_factory(
            action='read', record=record, cls=DepositPermission),
        update_permission_factory_imp=lambda record: record_permission_factory(
            action='update', record=record, cls=DepositPermission),
        delete_permission_factory_imp=lambda record: record_permission_factory(
            action='delete', record=record, cls=DepositPermission),
        list_permission_factory_imp=lambda record: record_permission_factory(
            action='list', record=record, cls=DepositPermission)),
}

# Add endpoint for collections
RECORDS_REST_ENDPOINTS['coll'] = CollectionConfiguration.rest_endpoint

# Add endpoint for subdivisions
RECORDS_REST_ENDPOINTS['subd'] = SubdivisionConfiguration.rest_endpoint
"""REST endpoints."""

DEFAULT_AGGREGATION_SIZE = 50
"""Default size for aggregations."""

RECORDS_REST_FACETS = {
    'documents':
    dict(aggs=dict(
        subdivision=dict(terms=dict(field='subdivisions.pid',
                                    size=DEFAULT_AGGREGATION_SIZE)),
        organisation=dict(terms=dict(field='organisation.pid',
                                     size=DEFAULT_AGGREGATION_SIZE)),
        language=dict(
            terms=dict(field='language.value', size=DEFAULT_AGGREGATION_SIZE)),
        subject=dict(
            terms=dict(field='facet_subjects', size=DEFAULT_AGGREGATION_SIZE)),
        collection=dict(terms=dict(field='collections.pid',
                                   size=DEFAULT_AGGREGATION_SIZE)),
        document_type=dict(
            terms=dict(field='documentType', size=DEFAULT_AGGREGATION_SIZE)),
        controlled_affiliation=dict(
            terms=dict(field='contribution.controlledAffiliation.raw',
                       size=DEFAULT_AGGREGATION_SIZE)),
        author=dict(terms=dict(field='contribution.agent.preferred_name.raw',
                               size=DEFAULT_AGGREGATION_SIZE)),
        year=dict(date_histogram=dict(
            field='provisionActivity.startDate',
            interval='year',
            format='yyyy',
        )),
        customField1=dict(terms=dict(field='customField1.raw',
                                     size=DEFAULT_AGGREGATION_SIZE)),
        customField2=dict(terms=dict(field='customField2.raw',
                                     size=DEFAULT_AGGREGATION_SIZE)),
        customField3=dict(terms=dict(field='customField3.raw',
                                     size=DEFAULT_AGGREGATION_SIZE))),
         filters={
             'subdivision':
             and_term_filter('subdivisions.pid'),
             'organisation':
             and_term_filter('organisation.pid'),
             'language':
             and_term_filter('language.value'),
             'subject':
             and_term_filter('facet_subjects'),
             'collection':
             and_term_filter('collections.pid'),
             'document_type':
             and_term_filter('documentType'),
             'controlled_affiliation':
             and_term_filter('contribution.controlledAffiliation.raw'),
             'author':
             and_term_filter('contribution.agent.preferred_name.raw'),
             'year':
             range_filter('provisionActivity.startDate',
                          format='yyyy',
                          end_date_math='/y'),
             'open_access':
             and_term_filter('isOpenAccess'),
             'customField1':
             and_term_filter('customField1.raw'),
             'customField2':
             and_term_filter('customField2.raw'),
             'customField3':
             and_term_filter('customField3.raw')
         }),
    'deposits':
    dict(aggs=dict(
        subdivision=dict(terms=dict(field='diffusion.subdivisions.pid',
                                    size=DEFAULT_AGGREGATION_SIZE)),
        status=dict(terms=dict(field='status', size=DEFAULT_AGGREGATION_SIZE)),
        user=dict(terms=dict(field='user.pid', size=DEFAULT_AGGREGATION_SIZE)),
        contributor=dict(terms=dict(field='facet_contributors',
                                    size=DEFAULT_AGGREGATION_SIZE))),
         filters={
             'subdivision': and_term_filter('diffusion.subdivisions.pid'),
             _('pid'): and_term_filter('pid'),
             _('status'): and_term_filter('status'),
             _('user'): and_term_filter('user.pid'),
             _('contributor'): and_term_filter('facet_contributors'),
         }),
    'users': {
        'aggs': {
            'missing_organisation': {
                'filter': {
                    'bool': {
                        'must_not': {
                            'exists': {
                                'field': 'organisation'
                            }
                        }
                    }
                }
            },
            'subdivision': {
                'terms': {
                    'field': 'subdivision.pid',
                    'size': DEFAULT_AGGREGATION_SIZE
                }
            }
        },
        'filters': {
            'missing_organisation': missing_field_filter('organisation'),
            'subdivision': and_term_filter('subdivision.pid')
        }
    }
}
"""REST search facets."""

INDEXES = ['documents', 'organisations', 'users', 'deposits']

RECORDS_REST_SORT_OPTIONS = {}
for index in INDEXES:
    RECORDS_REST_SORT_OPTIONS[index] = {
        'mostrecent': {
            'title': _('Most recent'),
            'fields': ['-_created'],
            'default_order': 'desc',
            'order': 1,
        },
        'bestmatch': {
            'title': _('Best match'),
            'fields': ['-_score'],
            'default_order': 'asc',
            'order': 2,
        }
    }
"""Setup sorting options."""

RECORDS_REST_DEFAULT_SORT = {}
for index in INDEXES:
    RECORDS_REST_DEFAULT_SORT[index] = {
        'query': 'bestmatch',
        'noquery': 'mostrecent'
    }
"""Set default sorting options."""

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'doc': '/files',
        'depo': '/files',
        'org': '/files',
        'coll': '/files'
    }
}

SONAR_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""

# OAUTH
# =====
OAUTHCLIENT_REMOTE_APPS = dict(orcid=orcid.REMOTE_APP)

ORCID_DOMAIN = os.environ.get('ORCID_CONSUMER_DOMAIN', 'sandbox.orcid.org')

OAUTHCLIENT_REMOTE_APPS['orcid']['signup_handler']['info'] = \
    'sonar.modules.oauth.orcid:account_info'
OAUTHCLIENT_REMOTE_APPS['orcid']['signup_handler']['setup'] = \
    'sonar.modules.oauth.orcid:account_setup'
OAUTHCLIENT_REMOTE_APPS['orcid']['params'].update(
    dict(
        base_url='https://pub.{domain}/'.format(domain=ORCID_DOMAIN),
        access_token_url='https://pub.{domain}/oauth/token'.format(
            domain=ORCID_DOMAIN),
        authorize_url='https://{domain}/oauth/authorize#show_login'.format(
            domain=ORCID_DOMAIN),
    ))

OAUTHCLIENT_SIGNUP_TEMPLATE = 'sonar/oauth/signup.html'

# Must be set as environment variable
ORCID_APP_CREDENTIALS = dict(
    consumer_key=os.environ.get('ORCID_CONSUMER_KEY', ''),
    consumer_secret=os.environ.get('ORCID_CONSUMER_SECRET', ''),
)

# Shibboleth authentication
# =========================
SHIBBOLETH_SERVICE_PROVIDER = dict(strict=True,
                                   debug=True,
                                   entity_id='https://sonar.ch/shibboleth')

SHIBBOLETH_IDENTITY_PROVIDERS = dict(
    eduidtest=dict(
        entity_id='https://test.eduid.ch/idp/shibboleth',
        title='SWITCH edu-ID test',
        dev=True,
        sso_url='https://login.test.eduid.ch/idp/profile/SAML2/Redirect/SSO',
        mappings=dict(
            email='urn:oid:0.9.2342.19200300.100.1.3',
            full_name='urn:oid:2.5.4.3',
            user_unique_id='urn:oid:2.16.756.1.2.5.1.1.1',
        )),
    eduid=dict(entity_id='https://eduid.ch/idp/shibboleth',
               title='SWITCH edu-ID',
               sso_url='https://login.eduid.ch/idp/profile/SAML2/Redirect/SSO',
               mappings=dict(
                   email='urn:oid:0.9.2342.19200300.100.1.3',
                   full_name='urn:oid:2.16.840.1.113730.3.1.241',
                   user_unique_id='urn:oid:2.16.756.1.2.5.1.1.1',
               )))
# For each IDP, there's a mapping to properties for matching result with local
# values. Email and full name will be used to create user account and
# user_unique_id is stored in database in an Oauth link.

# Admin layout
# =========================
ADMIN_BASE_TEMPLATE = 'sonar/page_admin.html'
ADMIN_PERMISSION_FACTORY = 'sonar.modules.permissions.admin_permission_factory'

REST_ENABLE_CORS = True
"""Enable CORS to make it possible to do request to API from other
applications."""

FILES_REST_PERMISSION_FACTORY = \
    'sonar.modules.permissions.files_permission_factory'

# Database
# =========================
DB_VERSIONING = False
# DB versioning is disabled globally, because of performances during documents
# importation.

# WIKI
# ====
WIKI_CONTENT_DIR = './wiki'
WIKI_URL_PREFIX = '/help'
WIKI_LANGUAGES = ['en', 'fr', 'de', 'it']
WIKI_CURRENT_LANGUAGE = get_current_language
WIKI_UPLOAD_FOLDER = os.path.join(WIKI_CONTENT_DIR, 'files')
WIKI_BASE_TEMPLATE = 'sonar/page_wiki.html'
WIKI_EDIT_VIEW_PERMISSION = wiki_edit_permission
WIKI_EDIT_UI_PERMISSION = wiki_edit_permission
WIKI_MARKDOWN_EXTENSIONS = set(('extra', ))

# PREVIEW
# =======
PREVIEWER_BASE_TEMPLATE = 'sonar/preview/base.html'
PREVIEWER_MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
"""Maximum file size in bytes for image files."""
PREVIEWER_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
"""Maximum file size in bytes for JSON/XML files."""

# OAI-PMH
# =======
#: Index to use for the OAI-PMH server.
OAISERVER_RECORD_INDEX = 'documents'
#: OAI identifier prefix
OAISERVER_ID_PREFIX = 'oai:sonar.ch:'
#: XSL file
OAISERVER_XSL_URL = 'static/xsl/oai2.xsl'
#: Export formats
OAISERVER_METADATA_FORMATS = {
    'oai_dc': {
        'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
        'serializer': 'sonar.modules.documents.serializers.oaipmh_oai_dc',
    }
}
#: Number of records to return per page in OAI-PMH results.
OAISERVER_PAGE_SIZE = 100

# Stats
# =====
STATS_EVENTS = {
    'file-download': {
        'signal':
        'invenio_files_rest.signals.file_downloaded',
        'templates':
        'invenio_stats.contrib.file_download',
        'event_builders':
        ['invenio_stats.contrib.event_builders.file_download_event_builder'],
        'cls':
        EventsIndexer,
        'params': {
            'preprocessors': [
                'invenio_stats.processors:flag_robots',
                # Don't index robot events
                lambda doc: doc if not doc['is_robot'] else None,
                'invenio_stats.processors:flag_machines',
                'invenio_stats.processors:anonymize_user',
                'invenio_stats.contrib.event_builders:build_file_unique_id',
            ],
            # Keep only 1 file download for each file and user every 30 sec
            'double_click_window':
            30,
            # Create one index per year which will store file download events
            'suffix':
            '%Y',
        }
    },
    'record-view': {
        'signal':
        'invenio_records_ui.signals.record_viewed',
        'templates':
        'invenio_stats.contrib.record_view',
        'event_builders':
        ['invenio_stats.contrib.event_builders.record_view_event_builder'],
        'cls':
        EventsIndexer,
        'params': {
            'preprocessors': [
                'invenio_stats.processors:flag_robots',
                # Don't index robot events
                lambda doc: doc if not doc['is_robot'] else None,
                'invenio_stats.processors:flag_machines',
                'invenio_stats.processors:anonymize_user',
                'invenio_stats.contrib.event_builders:build_record_unique_id',
            ],
            # Keep only 1 file download for each file and user every 30 sec
            'double_click_window':
            30,
            # Create one index per year which will store file download events
            'suffix':
            '%Y',
        },
    },
}
