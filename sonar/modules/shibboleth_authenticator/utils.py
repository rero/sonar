# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Utility methods to help find, authenticate or register a remote user."""

from __future__ import absolute_import, print_function

from urllib.parse import urlparse

import uritools
from flask import current_app, request
from slugify import slugify
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def get_account_info(attributes, remote_app):
    """Return account info for remote user.

    :param attributes: (dict) dictionary of data returned by identity provider.
    :param remote_app: (str) Identity provider key.
    :returns: (dict) A dictionary representing user to create or update.
    """
    mappings = current_app.config['SHIBBOLETH_IDENTITY_PROVIDERS'][remote_app][
        'mappings']

    # Map data according to configuration
    email = attributes[mappings['email']][0]
    external_id = attributes[mappings['user_unique_id']][0]
    full_name = attributes[mappings['full_name']][0]

    return dict(
        user=dict(
            email=email,
            profile=dict(full_name=full_name, username=slugify(full_name)),
        ),
        external_id=external_id,
        external_method=remote_app,
    )


def get_safe_redirect_target(arg='next'):
    """Get URL to redirect to and ensure that it is local.

    :param arg: (str) URL argument.
    :returns: (str|None) Redirect target or none.
    """
    for target in request.args.get(arg), request.referrer:
        if target:
            redirect_uri = uritools.urisplit(target)
            allowed_hosts = current_app.config.get('APP_ALLOWED_HOSTS', [])

            if redirect_uri.host in allowed_hosts:
                return target

            if redirect_uri.path:
                return uritools.uricompose(path=redirect_uri.path,
                                           query=redirect_uri.query)

    return None


def prepare_flask_request(flask_request):
    """
    Prepare flask request.

    :param flask_request: (flask.Request) Flask request.
    :returns: (dict) A dictionary containing request infos
    """
    url_data = urlparse(flask_request.url)

    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields.
    return {
        'https': 'on' if flask_request.scheme == 'https' else 'off',
        'http_host': flask_request.host,
        'server_port': url_data.port,
        'script_name': flask_request.path,
        'get_data': flask_request.args.copy(),
        'X-Forwarded-for': '',
        'post_data': flask_request.form.copy(),
    }
