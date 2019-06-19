# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Default configuration for Swiss Open Access Repository.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

import os
from datetime import timedelta

from invenio_indexer.api import RecordIndexer
from invenio_oauthclient.contrib import orcid
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, check_elasticsearch

from sonar.modules.documents.api import DocumentRecord, DocumentSearch
from sonar.modules.institutions.api import InstitutionRecord, InstitutionSearch


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/3'

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    ('fr', _('French')),
    ('de', _('German')),
    ('it', _('Italian'))
]

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
THEME_LOGO = 'images/sonar-logo.svg'

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
    "Welcome to Swiss Open Access Repository!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = 'redis://localhost:6379/1'
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True


# User profiles
# =============
USERPROFILES_EXTEND_SECURITY_FORMS = True


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
}

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

SEARCH_UI_SEARCH_INDEX = 'documents'
SEARCH_UI_SEARCH_API = '/api/documents/'
SEARCH_UI_SEARCH_TEMPLATE = 'sonar/search.html'

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/documents/search_ui/results.html'
SEARCH_UI_JSTEMPLATE_COUNT = 'templates/documents/search_ui/count.html'
SEARCH_UI_JSTEMPLATE_PAGINATION = 'templates/documents/search_ui/'\
                                  'pagination.html'
SEARCH_UI_JSTEMPLATE_SORT_ORDER = 'templates/documents/search_ui/'\
                                  'sort_order.html'
SEARCH_UI_JSTEMPLATE_SELECT_BOX = 'templates/documents/search_ui/'\
                                  'select_box.html'
SEARCH_UI_JSTEMPLATE_LOADING = 'templates/documents/search_ui/loading.html'
SEARCH_UI_JSTEMPLATE_FACETS = 'templates/documents/search_ui/facets.html'

SECURITY_LOGIN_USER_TEMPLATE = 'sonar/accounts/login.html'
SECURITY_FORGOT_PASSWORD_TEMPLATE = 'sonar/accounts/forgot_password.html'
SECURITY_REGISTER_USER_TEMPLATE = 'sonar/accounts/signup.html'

RECORDS_UI_ENDPOINTS = {
    'document': {
        'pid_type': 'doc',
        'route': '/organization/<ir>/documents/<pid_value>',
        'view_imp': 'sonar.modules.documents.views:detail'
    },
}
"""Records UI for sonar."""

RECORDS_REST_ENDPOINTS = {
    'doc': dict(
        pid_type='doc',
        pid_minter='document_id',
        pid_fetcher='document_id',
        default_endpoint_prefix=True,
        record_class=DocumentRecord,
        search_class=DocumentSearch,
        indexer_class=RecordIndexer,
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
        item_route='/documents/<pid(doc):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
        list_permission_factory_imp=allow_all
    ),
    'inst': dict(
        pid_type='inst',
        pid_minter='institution_id',
        pid_fetcher='institution_id',
        default_endpoint_prefix=True,
        record_class=InstitutionRecord,
        search_class=InstitutionSearch,
        indexer_class=RecordIndexer,
        search_index='institutions',
        search_type=None,
        record_serializers={
            'application/json': ('sonar.modules.institutions.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('sonar.modules.institutions.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('sonar.modules.institutions.loaders'
                                 ':json_v1'),
        },
        list_route='/institutions/',
        item_route='/institutions/<pid(inst):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
        list_permission_factory_imp=allow_all
    )
}
"""REST endpoints."""

RECORDS_REST_FACETS = {
    'documents': dict(
        aggs=dict(
            institution=dict(terms=dict(field='institution.pid')),
            language=dict(terms=dict(field='languages.name')),
            author=dict(terms=dict(field='facet_authors')),
            subject=dict(terms=dict(field='facet_subjects'))
        ),
        filters={
            _('institution'): terms_filter('institution.pid'),
            _('language'): terms_filter('languages.name'),
            _('author'): terms_filter('facet_authors'),
            _('subject'): terms_filter('facet_subjects'),
        }
    )
}
"""REST search facets."""

RECORDS_REST_SORT_OPTIONS = dict(
    documents=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=2,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=1,
        ),
    )
)
"""Setup sorting options."""

RECORDS_REST_DEFAULT_SORT = dict(
    documents=dict(
        query='bestmatch',
        noquery='mostrecent',
    ),
)
"""Set default sorting options."""

SONAR_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""

JSONSCHEMAS_RESOLVE_SCHEMA = True
JSONSCHEMAS_REPLACE_REFS = True


# OAUTH
# =====
OAUTHCLIENT_REMOTE_APPS = dict(orcid=orcid.REMOTE_APP)

ORCID_DOMAIN = 'sandbox.orcid.org'

OAUTHCLIENT_REMOTE_APPS['orcid']['signup_handler']['info'] = \
    'sonar.modules.oauth.orcid:account_info'
OAUTHCLIENT_REMOTE_APPS['orcid']['signup_handler']['setup'] = \
    'sonar.modules.oauth.orcid:account_setup'
OAUTHCLIENT_REMOTE_APPS['orcid']['params'].update(
    dict(
        base_url='https://pub.{domain}/'.format(domain=ORCID_DOMAIN),
        access_token_url='https://pub.{domain}/oauth/token'.format(
            domain=ORCID_DOMAIN
        ),
        authorize_url='https://{domain}/oauth/authorize#show_login'.format(
            domain=ORCID_DOMAIN
        ),
    )
)

OAUTHCLIENT_SIGNUP_TEMPLATE = 'sonar/oauth/signup.html'

# Must be set as environment variable
ORCID_APP_CREDENTIALS = dict(
    consumer_key=os.environ.get('ORCID_CONSUMER_KEY', ''),
    consumer_secret=os.environ.get('ORCID_CONSUMER_SECRET', ''),
)

# Shibboleth authentication
# =========================
SHIBBOLETH_SERVICE_PROVIDER = dict(
    strict=True,
    debug=True,
    entity_id='https://sonar.ch/shibboleth'
)

SHIBBOLETH_IDENTITY_PROVIDERS = dict(
    eduidtest=dict(
        entity_id='https://test.eduid.ch/idp/shibboleth',
        title='SWITCH edu-ID test',
        sso_url='https://login.test.eduid.ch/idp/profile/SAML2/Redirect/SSO',
        mappings=dict(
            email='urn:oid:0.9.2342.19200300.100.1.3',
            full_name='urn:oid:2.5.4.3',
            user_unique_id='urn:oid:2.16.756.1.2.5.1.1.1',
        )
    )
)
