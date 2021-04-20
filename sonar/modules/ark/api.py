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


"""ARK API."""

import requests
import xmltodict
from flask import current_app
from requests.auth import HTTPBasicAuth
from werkzeug.local import LocalProxy


class NMAServerError(Exception):
    """Remote NMA server error."""


class NMAUnauthorizedError(Exception):
    """Bad credential for the remote NAM server."""


def check_http_status(valid_status):
    """Check the http status returned by the remote server.

    :param valid_status: A list of valid HTTP status.
    :returns: The wrapper function, see python decorator.
    """
    def decorator(func):
        """Decorator.

        :param func: The input function to decorate.
        :returns: The wrapper function, see python decorator.
        """
        def wrapper(*args, **kwargs):
            """This is the wrapper function for decorator.

            :param args: All the parameters as key value.
            :param kwargs: All the parameters as dict.
            :returns: The wrapper function, see python decorator.
            """
            status_code, content = func(*args, **kwargs)
            if status_code == 401:
                raise NMAUnauthorizedError(
                    f'The server returns an unauthorized status,'
                    f' msg: {content}.'
                )
            if status_code not in valid_status:
                raise NMAServerError( # pragma: no cover
                    f'The server returns an invalid status('\
                    f'{status_code}), msg: {content}')
            if isinstance(content, str):
                content = content.strip()
                content = content.replace('success: ', '')
            return content
        return wrapper
    return decorator

class Ark:
    """ARK Client for arketype.ch.

    More details: https://www.arketype.ch/doc/apidoc.html.
    """

    def __init__(self):
        """Constructor."""
        self.init_config()
        self._url_status = f'{self._nma}/status'
        self._url_get = f'{self._nma}/id'
        self._url_login = f'{self._nma}/login'
        self._url_minter = \
            f'{self._nma}/shoulder/{self._scheme}/{self._naan}/{self._shoulder}'
        self._url_resolve = self._resolver

    def config(self):
        """String representation with config and urls."""
        return f"""
config:
    user: {self._user}
    password: {self._password}
    resolver: {self._resolver}
    nma: {self._nma}
    naan: {self._naan}
    scheme: {self._scheme}
    shoulder: {self._shoulder}
urls:
    get: {self._url_get}
    minter: {self._url_minter}
    status: {self._url_status}
    login: {self._url_login}
    resolve: {self._url_resolve}

"""

    def init_config(self):
        """Read the configuation from the current app."""
        config = current_app.config
        for conf_key in config.keys():
            if conf_key.startswith('SONAR_APP_ARK_'):
                setattr(self,
                        conf_key.replace('SONAR_APP_ARK', '').lower(),
                        config.get(conf_key))

    def ark_from_id(self, _id):
        """Translate an ARK from an id.

        :returns: an ARK identifier.
        """
        return f'{self._scheme}/{self._naan}/{self._shoulder}{_id}'

    def resolver_url(self, _id):
        """Translate an ARK from an id.

        :param _id: The record identifier.
        :returns: The URL to resolve the given identifier.
        """
        ark_id = self.ark_from_id(_id)
        return f'{self._url_resolve}/{ark_id}'

    def target_url(self, pid, view='global'):
        """Create an ARK target url from an record pid.

        :param pid: The record persistant identifier.
        :param view: The organisiation view code.
        """
        cfg = current_app.config
        host_name = 'https://' + cfg.get('JSONSCHEMAS_HOST')
        return '/'.join([host_name, view, 'documents', pid])

    @check_http_status(valid_status=[200])
    def status(self):
        """Get the ARK server status."""
        response = requests.get(self._url_status)
        return response.status_code, response.text

    @check_http_status(valid_status=[200])
    def login(self):
        """Test the credentials on the ARK server.

        :returns: A tuple of the HTTP status code and the text response.
        """
        response = requests.get(
            self._url_login,
            auth=HTTPBasicAuth(self._user, self._password)
        )
        return response.status_code, response.text

    @check_http_status(valid_status=[200, 400])
    def get(self, pid):
        """Get the information given an identifier.

        :param pid: The record persistant identifier.
        :returns: A tuple of the HTTP status code and the server response as
                  dict.
        """
        url = f'{self._url_get}/{self._scheme}/{self._naan}/{self._shoulder}{pid}'
        response = requests.get(url)
        data = {}
        if response.status_code != 400:
            for line in response.text.split('\n'):
                if line:
                    key, value = line.split(': ', 1)
                    if key in ['datacite']:
                        data[key] = xmltodict.parse(value.replace('%0A',' '))
                    else:
                        data[key] = value
        return response.status_code, data

    @check_http_status(valid_status=[302])
    def resolve(self, pid):
        """Resolve an ARK and return the target.

        :param pid: The record persistant identifier.
        :returns: A tuple of the HTTP status code and the target URL.
        """
        url = self.resolver_url(pid)
        response = requests.get(url, allow_redirects=False)
        return response.status_code, response.headers.get('Location')

    @check_http_status(valid_status=[201])
    def create(self, pid, target, update_if_exists='yes'):
        """Create a new ARK with a given id.

        :param pid: The record persistant identifier.
        :param target: The ARK target URL.
        :param update_if_exists: If True update instead of create.
        :returns: A tuple of the HTTP status code and the text response.
        """
        ark_id = self.ark_from_id(pid)
        url = f'{self._url_get}/{ark_id}?update_if_exists={update_if_exists}'
        response = requests.put(
            url,
            auth=HTTPBasicAuth(self._user, self._password),
            data=f'_target: {target}'
        )
        return response.status_code, response.text


    @check_http_status(valid_status=[201])
    def mint(self, target):
        """Generate and register a new ARK id.

        :param target: The ARK target URL.
        :returns: A tuple of the HTTP status code and the text response.
        """
        response = requests.post(
            self._url_minter,
            auth=HTTPBasicAuth(self._user, self._password),
            data=f'_target: {target}')
        return response.status_code, response.text

    @check_http_status(valid_status=[200])
    def update(self, pid, target):
        """Update the given ARK.

        :param pid: The record persistant identifier.
        :param target: The ARK target URL.
        :returns: A tuple of the HTTP status code and the text response.
        """
        ark_id = self.ark_from_id(pid)
        url = f'{self._url_get}/{ark_id}'
        response = requests.post(
            url,
            auth=HTTPBasicAuth(self._user, self._password),
            data=f'_target: {target}\n_status: public'
        )
        return response.status_code, response.text

    @check_http_status(valid_status=[200])
    def delete(self, pid):
        """Mark an ARK as unavailable.

        :param pid: The record persistant identifier.
        :returns: A tuple of the HTTP status code and the text response.
        """
        ark_id = self.ark_from_id(pid)
        url = f'{self._url_get}/{ark_id}'
        response = requests.post(
            url,
            auth=HTTPBasicAuth(self._user, self._password),
            data=f'_status: unavailable | removed'
        )
        return response.status_code, response.text


# proxy on the ARK API if it is enable
current_ark = LocalProxy(
    lambda: Ark() if current_app.config.get('SONAR_APP_ARK_NMA') else None)
