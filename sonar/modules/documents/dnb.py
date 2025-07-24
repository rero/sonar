# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Dnb URN service API."""

import base64
import json

import requests
from flask import current_app


class DnbServerError(Exception):
    """The Dnb Server returns an error."""


class DnbUrnService:
    """Dnb URN service class."""

    @classmethod
    def base_url(cls):
        """Base DBN URL.

        :rtype: str.
        :returns: the DBN base server URL.
        """
        return f"{current_app.config.get('SONAR_APP_URN_DNB_BASE_URL')}/urns"

    @classmethod
    def headers(cls):
        """Set headers for queries.

        :returns: headers dictionary.
        """
        username = current_app.config.get("SONAR_APP_URN_DNB_USERNAME")
        password = current_app.config.get("SONAR_APP_URN_DNB_PASSWORD")
        string = f"{username}:{password}"
        auth = base64.b64encode(string.encode()).decode("ascii")
        return {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def exists(cls, urn_code):
        """Check the existence for a URN.

        :param urn_code: the urn code.
        :returns: True if urn is exists, otherwise False.
        """
        # Documentation: https://wiki.dnb.de/display/URNSERVDOK/URN-Service+API
        # https://wiki.dnb.de/display/URNSERVDOK/Beispiele%3A+URN-Verwaltung
        try:
            response = requests.request(
                "HEAD", f"{cls.base_url()}/urn/{urn_code}", headers=cls.headers()
            )
            if not response.status_code in [200, 404]:
                raise DnbServerError(
                    f"Bad DNB server response status {response.status_code}, "
                    f"when we check the existence of the following "
                    f"urn: {urn_code}"
                )
            return response.status_code == 200
        except Exception as error:
            raise DnbServerError(error)

    @classmethod
    def get_urls(cls, urn_code):
        """Get the URN information.

        :param urn_code: the urn code.
        :returns: the raw server data.
        """
        # Documentation: https://wiki.dnb.de/display/URNSERVDOK/URN-Service+API
        # https://wiki.dnb.de/display/URNSERVDOK/Beispiele%3A+URN-Verwaltung
        try:
            response = requests.get(
                f"{cls.base_url()}/urn/{urn_code}/urls", headers=cls.headers()
            )
            if not response.status_code == 200:
                raise DnbServerError(
                    f"Bad DNB server response status {response.status_code}, "
                    f"when we get the information of the following "
                    f"urn: {urn_code}"
                )
            return response.json()
        except Exception as error:
            raise DnbServerError(error)

    @classmethod
    def get(cls, urn_code):
        """Get the URN information.

        :param urn_code: the urn code.
        :rtype: dict.
        :returns: the raw data from the server.
        """
        # Documentation: https://wiki.dnb.de/display/URNSERVDOK/URN-Service+API
        # https://wiki.dnb.de/display/URNSERVDOK/Beispiele%3A+URN-Verwaltung
        answer = False
        try:
            response = requests.get(
                f"{cls.base_url()}/urn/{urn_code}", headers=cls.headers()
            )
            if response.status_code != 200:
                raise DnbServerError(
                    f"Bad DNB server response status {response.status_code}, "
                    f"when we get the information of the following "
                    f"urn: {urn_code}"
                )
            return response.json()
        except Exception as error:
            raise DnbServerError(error) from error

    @classmethod
    def update(cls, urn_code, urls):
        """Update the list of urs registered to a given URN.

        :param urn_code: the urn code.
        :param urls: list of str - list of the target URL.

        """
        response = requests.request(
            "PATCH",
            f"{cls.base_url()}/urn/{urn_code}/my-urls",
            headers=cls.headers(),
            data=json.dumps(urls),
        )
        if response.status_code != 204:
            raise DnbServerError(
                f"Bad DNB server response status {response.status_code}, "
                f"when we update the information of the following "
                f"urn: {urn_code}"
            )

    @classmethod
    def set_successor(cls, urn_code, successor_urn):
        """Set the successor of a given urn.

        :param urn_code: str - the urn code.
        :param successor_urn: str - the urn code of the successor.
        """
        response = requests.request(
            "PATCH",
            f"{cls.base_url()}/urn/{urn_code}",
            headers=cls.headers(),
            data=json.dumps(dict(successor=f"{cls.base_url()}/urn/{successor_urn}")),
        )
        if response.status_code != 204:
            msg = response.json().get("developerMessage", "")
            raise DnbServerError(
                f"Bad DNB server response status {response.status_code}, "
                f"when we update the information of the following "
                f"urn: {urn_code}",
                f"{msg}",
            )

    @classmethod
    def create(cls, data):
        """Register a new URN to the DBN service with a list of urls.

        :param data: dict - the request body see https://tinyurl.com/mtpfaz5z
                     for more details.
        """
        response = requests.request(
            "POST", cls.base_url(), headers=cls.headers(), data=json.dumps(data)
        )
        if response.status_code != 201:
            raise DnbServerError(
                f"Bad DNB server response status {response.status_code}, "
                f"when we update the information of the following "
                f'urn: {data.get("urn")}'
            )

    @classmethod
    def register_document(cls, document):
        """Register a new URN code.

        :param document: the document.
        :returns: True if urn is registered, otherwise False.
        """
        from sonar.modules.documents.api import DocumentRecord

        if not isinstance(document, DocumentRecord):
            document = DocumentRecord(document)
        if url := cls.get_url(document):
            urn = document.get_rero_urn_code(document)
            data = {"urn": urn, "urls": [{"url": url, "priority": 1}]}
            if cls.exists(urn):
                cls.update(urn, data["urls"])
            else:
                cls.create(data)
            return True
        return False

    @classmethod
    def get_url(cls, document):
        """Get the target url depending to the organization.

        :param document: Document - the document containing the URN.
        :rtype: str.
        :returns: the target URL.
        """
        base_url = f'https://{current_app.config.get("SONAR_APP_SERVER_NAME")}'
        if orgs := document.resolve().get("organisation", []):
            org_code = current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION")
            if org := orgs[0]:
                if org.get("isDedicated") or org.get("isShared"):
                    org_code = org.get("code")
                if org.get("isDedicated") and (server_name := org.get("serverName")):
                    base_url = f"https://{server_name}"
            return f"{base_url}/{org_code}/documents/{document.get('pid')}"
