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

from sonar.modules.documents.api import DocumentRecord


class DnbUrnService:
    """Dnb URN service class."""

    @classmethod
    def headers(cls):
        """Set headers for queries.

        :returns: headers dictionary.
        """
        username = current_app.config.get('SONAR_APP_URN_DNB_USERNAME')
        password = current_app.config.get('SONAR_APP_URN_DNB_PASSWORD')
        string = f"{username}:{password}"
        auth = base64.b64encode(string.encode()).decode('ascii')
        return {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    @classmethod
    def verify(cls, urn_code):
        """Verify the existence for a URN.

        :param urn_code: the urn code.
        :returns: True if urn is registered, otherwise False.
        """
        # Documentation: https://wiki.dnb.de/display/URNSERVDOK/URN-Service+API
        # https://wiki.dnb.de/display/URNSERVDOK/Beispiele%3A+URN-Verwaltung
        answer = False
        try:
            response = requests.request(
                'HEAD',
                f"{current_app.config.get('SONAR_APP_URN_DNB_BASE_URL')}"\
                f"/urns/urn/{urn_code}",
                headers=cls.headers()
            )
            answer = response.status_code == 200
        except Exception as error:
            current_app.logger.error(
                'unable to connect to DNB verify service.')
        return answer


    @classmethod
    def register_document(cls, document):
        """Register a new URN code.

        :param document: the document.
        :returns: True if urn is registered, otherwise False.
        """
        from sonar.modules.documents.api import DocumentRecord
        from sonar.modules.organisations.api import OrganisationRecord
        answer = False
        sonar_base_url = current_app.config.get('SONAR_APP_BASE_URL')
        if not isinstance(document, DocumentRecord):
            document = DocumentRecord(document)
        if orgs := document.get('organisation', []):
            org_code = current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION')
            if org := orgs[0]:
                org = OrganisationRecord(org)
                org = org.replace_refs()
                if org.get('isDedicated') or org.get('isShared'):
                    org_code = org.get('code')
            url = f"{sonar_base_url}/{org_code}/documents/{document.get('pid')}"
            data = {
                'urn': document.get_rero_urn_code(document),
                'urls': [
                    {
                        'url': url,
                        'priority': 1
                    }
                ]
            }
            try:
                response = requests.request(
                    'POST',
                    f"{current_app.config.get('SONAR_APP_URN_DNB_BASE_URL')}/urns",
                    headers=cls.headers(),
                    data=json.dumps(data)
                )
                answer = response.status_code == 201
            except Exception as error:
                current_app.logger.error(
                    'unable to connect to DNB register service.')
        return answer


    @classmethod
    def register(cls, urn_code):
        """Register a new URN code.

        :param urn_code: the urn code.
        :returns: True if urn is registered, otherwise False.
        """
        identifiers = [{'type': 'bf:Urn', 'value': urn_code}]
        document = DocumentRecord.get_record_by_identifier(
            identifiers, ['bf:Urn'])
        return cls.register_document(document)
