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

import re

from flask import current_app
from invenio_pidstore.models import (
    PersistentIdentifier,
    PIDDoesNotExistError,
    PIDStatus,
)


class Ark:
    """ARK Management API."""

    def __new__(cls, naan="99999"):
        """Constructor.

        :returns: None if the configuration is not complete.
        :rtype: new Ark instance.
        """
        cls.init_config()
        if naan and cls._scheme and cls._shoulder and cls._resolver:
            cls._naan = naan
            cls._url_resolve = cls._resolver
            cls._regex = re.compile(
                rf"{cls._scheme}/{cls._naan}/{cls._shoulder}(?P<pid>\w+)"
            )
            return super(Ark, cls).__new__(cls)

    def config(self):
        """String representation with config and urls."""
        return f"""
config:
    resolver: {self._resolver}
    scheme: {self._scheme}
    shoulder: {self._shoulder}
    naan: {self._naan}
"""

    @classmethod
    def init_config(cls):
        """Read the configuation from the current app."""
        config = current_app.config
        for conf_key in config.keys():
            if conf_key.startswith("SONAR_APP_ARK_"):
                setattr(
                    cls,
                    conf_key.replace("SONAR_APP_ARK", "").lower(),
                    config.get(conf_key),
                )

    def ark_from_id(self, pid):
        """Translate an ARK from an id.

        :returns: an ARK identifier.
        """
        return f"{self._scheme}/{self._naan}/{self._shoulder}{pid}"

    def resolver_url(self, pid):
        """Translate an ARK from an id.

        :param pid: The record identifier.
        :returns: The URL to resolve the given identifier.
        """
        ark_id = self.ark_from_id(pid)
        return f"{self._url_resolve}/{ark_id}"

    def resolve(self, ark_id):
        """Resolve an ARK and return the target.

        :param ark_id: An ark identifier.
        :returns: The related document pid.
        """
        if match := self._regex.match(ark_id):
            return match.groupdict().get("pid")

    def get(self, _id):
        """Get the persistent identifier.

        :params _id: the document pid or an ARK id.
        :returns: the persistent identifier.
        :rtype: invenio persistent identifier instance.
        """
        if not self._regex.match(_id):
            _id = self.ark_from_id(_id)
        try:
            return PersistentIdentifier.get("ark", _id)
        except PIDDoesNotExistError:
            return None

    def create(self, pid, record_uuid):
        """Create a new ARK with a given id.

        :param pid: The record persistant identifier.
        :param target: The ARK target URL.
        :param update_if_exists: If True update instead of create.
        :returns: A tuple of the HTTP status code and the text response.
        """
        ark_id = self.ark_from_id(pid)
        pid = PersistentIdentifier.create(
            "ark",
            ark_id,
            object_type="rec",
            object_uuid=record_uuid,
            status=PIDStatus.REGISTERED,
        )
        return pid
