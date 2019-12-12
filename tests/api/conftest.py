# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Pytest fixtures and plugins for the API application."""

from __future__ import absolute_import, print_function

import pytest
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers, Role
from invenio_accounts.ext import hash_password
from invenio_app.factory import create_api

from sonar.modules.deposits.api import DepositRecord
from sonar.modules.users.api import UserRecord


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_api


@pytest.fixture()
def user_fixture(app, db):
    """Create user in database."""
    data = {
        'email': 'user@rero.ch',
        'first_name': 'John',
        'last_name': 'Doe',
        'roles': ['user']
    }

    user = UserRecord.create(data, dbcommit=True)
    user.reindex()
    db.session.commit()

    return user


@pytest.fixture()
def moderator_fixture(app, db):
    """Create moderator in database."""
    data = {
        'email': 'moderator@rero.ch',
        'first_name': 'John',
        'last_name': 'Doe',
        'roles': ['moderator']
    }

    user = UserRecord.create(data, dbcommit=True)
    user.reindex()
    db.session.commit()

    return user


@pytest.fixture()
def deposit_fixture(app, db, user_fixture):
    """Create a deposit."""
    data = {
        'status': 'in progress',
        'step': 'diffusion',
        'metadata': {
            'title': 'Title of deposit',
            'languages': ['fre']
        },
        'user': {
            '$ref':
            'https://sonar.ch/api/users/{pid}'.format(pid=user_fixture['pid'])
        }
    }

    deposit = DepositRecord.create(data, dbcommit=True, with_bucket=False)
    deposit.reindex()
    db.session.commit()
    return deposit
