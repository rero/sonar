# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Pytest fixtures and plugins for the UI application."""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_ui
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from orcid import PublicAPI


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_ui


@pytest.fixture(scope='module')
def orcid_record():
    """ORCID returned record."""
    return {
        'name': 'John Doe',
        'expires_in': 3599,
        'orcid': '0000-0000-0000-0000',
        'access_token': '123456',
        'refresh_token': 'test_refresh_token',
        'scope': '/authenticate',
        'token_type': 'bearer',
    }


@pytest.fixture(scope='module')
def user_record():
    """User record."""
    return dict(
        external_id='0000-0000-0000-0000',
        external_method='orcid',
        user=dict(
            email='john.doe@test.com',
            profile=dict(full_name='John Doe', username='john-doe'),
        ),
    )


@pytest.fixture(scope='module')
def models_fixture(app):
    """Flask app with example data used to test models."""
    with app.app_context():
        datastore = app.extensions['security'].datastore
        datastore.create_user(email='john.doe@test.com',
                              password='123456',
                              active=True)
        datastore.commit()


@pytest.fixture(scope='module')
def remote_account_fixture(app, models_fixture):
    """Create a remote token from user data."""
    datastore = app.extensions['security'].datastore
    user = datastore.find_user(email='john.doe@test.com')

    remote_account = RemoteAccount.create(1, 'dev', dict())
    remote_token = RemoteToken.create(user.id, 'dev', 'token', 'secret')

    return remote_account, remote_token


@pytest.fixture
def mock_api_read_record(monkeypatch):
    """Mock the call to api for retrieving record details."""
    def read_record_public(method, record_id, request_type, token):
        record = {
            'orcid-identifier': {
                'path': '0000-0000-0000-0000',
            },
            'person': {
                'name': {
                    'given-names': {
                        'value': 'John'
                    },
                    'family-name': {
                        'value': 'Doe'
                    },
                },
                'emails': {
                    'email': [{
                        'email': 'john.doe@test.com',
                    }],
                }
            }
        }

        if (request_type == 'FAKE' or record_id == 'NOT_EXISTING' or
                token == 'NOT_EXISTING'):
            return None

        if request_type == 'person':
            return record['person']

        return record

    monkeypatch.setattr(PublicAPI, 'read_record_public', read_record_public)
