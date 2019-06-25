# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record providers."""

from __future__ import absolute_import, print_function

from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus, RecordIdentifier
from invenio_pidstore.providers.base import BaseProvider


class Provider(BaseProvider):
    """Record provider."""

    pid_type = None
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.

    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.RESERVED
    """Record IDs are by default reserved.
    Default: :attr:`invenio_pidstore.models.PIDStatus.RESERVED`
    """

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier.

        Note: if the object_type and object_uuid values are passed, then the
        PID status will be automatically setted to
        :attr:`invenio_pidstore.models.PIDStatus.REGISTERED`.
        :param object_type: The object type. (Default: None.)
        :param object_uuid: The object identifier. (Default: None).
        :param kwargs: You specify the pid_value.
        """
        # PID value not already exists, generating a new one
        if not kwargs.get("pid_value"):
            kwargs["pid_value"] = str(RecordIdentifier.next())

        kwargs.setdefault("status", cls.default_status)
        if object_type and object_uuid:
            kwargs["status"] = PIDStatus.REGISTERED

        try:
            # Try to retreive PID
            return cls.get(kwargs["pid_value"], cls.pid_type)
        except PIDDoesNotExistError:
            # Set default status
            kwargs.setdefault("status", cls.default_status)

            # if record is registered, change PID status
            if object_type and object_uuid:
                kwargs["status"] = PIDStatus.REGISTERED

            # Call base provider
            return super(Provider, cls).create(
                object_type=object_type, object_uuid=object_uuid, **kwargs
            )
