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
from onelogin.saml2.auth import OneLogin_Saml2_Auth

import sonar.modules.shibboleth_authenticator.auth as auth


def test_get_identity_provider_configuration(app):
    """Test get identity provider."""
    # Identity provider not found in configuration
    with pytest.raises(Exception) as e:
        auth.get_identity_provider_configuration("not_exists")
    assert str(e.value) == 'Identity provider not found for "not_exists"'

    # Valid identity provider
    assert auth.get_identity_provider_configuration("idp").get("entity_id") == "https://idp.com/shibboleth"


def test_init_saml_auth(app, request):
    """Test SAML auth initialization."""
    # Valid init without strict mode
    app.config.update(
        SHIBBOLETH_SERVICE_PROVIDER={
            "debug": True,
            "entity_id": "entity_id",
            "x509cert": "./docker/nginx/sp.pem",
            "private_key": "./docker/nginx/sp.key",
        }
    )
    assert isinstance(auth.init_saml_auth(request, "idp"), OneLogin_Saml2_Auth)

    # Valid init without debug
    app.config.update(
        SHIBBOLETH_SERVICE_PROVIDER={
            "strict": True,
            "entity_id": "entity_id",
            "x509cert": "./docker/nginx/sp.pem",
            "private_key": "./docker/nginx/sp.key",
        }
    )
    assert isinstance(auth.init_saml_auth(request, "idp"), OneLogin_Saml2_Auth)

    # Init failed caused by certificate lack
    app.config.update(
        SHIBBOLETH_SERVICE_PROVIDER={
            "debug": True,
            "strict": True,
            "entity_id": "entity_id",
            "private_key": "./docker/nginx/sp.key",
        }
    )
    with pytest.raises(Exception) as e:
        auth.init_saml_auth(request, "idp")
    assert str(e.value) == '"x509cert" path for service provider not configured'

    # Init failed caused by private key lack
    app.config.update(
        SHIBBOLETH_SERVICE_PROVIDER={
            "debug": True,
            "strict": True,
            "entity_id": "entity_id",
            "x509cert": "./docker/nginx/sp.pem",
        }
    )
    with pytest.raises(Exception) as e:
        auth.init_saml_auth(request, "idp")
    assert str(e.value) == '"private_key" path for service provider not configured'

    # Init failed caused by entity ID lack
    app.config.update(
        SHIBBOLETH_SERVICE_PROVIDER={
            "debug": True,
            "strict": True,
            "x509cert": "./docker/nginx/sp.pem",
            "private_key": "./docker/nginx/sp.key",
        }
    )
    with pytest.raises(Exception) as e:
        auth.init_saml_auth(request, "idp")
    assert str(e.value) == '"entityId" for service provider not configured'
