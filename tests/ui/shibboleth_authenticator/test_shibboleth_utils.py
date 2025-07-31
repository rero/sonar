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

"""Test authenticator utils."""

import pytest

from sonar.modules.shibboleth_authenticator.utils import (
    get_account_info,
    get_safe_redirect_target,
    prepare_flask_request,
)


def test_accountinfo(app, valid_attributes):
    """Test get_account_info."""
    # Test valid result.
    res = get_account_info(valid_attributes, "idp")
    assert res
    assert res["user"]["email"] == "john.doe@test.com"

    # Test invalid remote app.
    with pytest.raises(KeyError):
        res = get_account_info(valid_attributes, "invalid")


def test_get_safe_redirect_target(app, monkeypatch):
    """Test safe redirect target."""
    app.config.update(APP_ALLOWED_HOSTS=["sonar.ch"])
    url1 = "/test/page"
    url2 = "https://sonar.ch/path/subpath?parameter=test"
    url3 = "http://test.ch/path/subpath?parameter=test"

    class MockRequest(object):
        """Mock request."""

        def __init__(self):
            self.args = dict(next=None)
            self.referrer = None

    mock_request = MockRequest()

    monkeypatch.setattr(
        "sonar.modules.shibboleth_authenticator.utils.request", mock_request
    )

    mock_request.args["next"] = url1
    assert get_safe_redirect_target() == url1

    mock_request.args["next"] = url2
    assert get_safe_redirect_target() == url2

    mock_request.args["next"] = url3
    assert get_safe_redirect_target() == "/path/subpath?parameter=test"

    mock_request.args["next"] = None
    assert not get_safe_redirect_target()


def test_prepare_flask_request(app):
    """Test flask request preparation."""

    class MockRequest(object):
        """Mock request."""

        url = "https://sonar.ch/test/page?parameter=test"
        host = "sonar.ch"
        scheme = "https"
        path = "/test/page"
        args = dict(parameter="test")
        form = dict()

    mock_request = MockRequest()

    assert prepare_flask_request(mock_request) == {
        "https": "on",
        "http_host": "sonar.ch",
        "server_port": None,
        "script_name": "/test/page",
        "get_data": {"parameter": "test"},
        "X-Forwarded-for": "",
        "post_data": {},
    }
