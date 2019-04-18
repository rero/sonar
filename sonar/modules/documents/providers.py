# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Document PID providers."""

from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider


class DocumentIdProvider(RecordIdProvider):
    """Document identifier provider."""

    pid_type = 'doc'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.

    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.REGISTERED
    """Record IDs are by default registered immediately."""
