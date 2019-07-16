# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Common pytest fixtures and plugins."""

import pytest
from flask import url_for
from flask_security.utils import encrypt_password


@pytest.fixture(scope='module', autouse=True)
def app_config(app_config):
    """Define configuration for module."""
    app_config['SHIBBOLETH_SERVICE_PROVIDER'] = dict(
        strict=True,
        debug=True,
        entity_id='entity_id',
        x509cert='./docker/nginx/sp.pem',
        private_key='./docker/nginx/sp.key')

    app_config['SHIBBOLETH_IDENTITY_PROVIDERS'] = dict(
        idp=dict(entity_id='https://idp.com/shibboleth',
                 sso_url='https://idp.com/Redirect/SSO',
                 mappings=dict(
                     email='email',
                     full_name='name',
                     user_unique_id='id',
                 )))

    return app_config


@pytest.fixture()
def create_user(app):
    """Create user in database."""
    datastore = app.extensions['security'].datastore
    datastore.create_user(email='john.doe@test.com',
                          password=encrypt_password('123456'),
                          active=True)
    datastore.commit()


@pytest.fixture()
def logged_user_client(create_user, client):
    """Log in user."""
    response = client.post(url_for('security.login'),
                           data=dict(email='john.doe@test.com',
                                     password='123456'))
    assert response.status_code == 302

    return client
