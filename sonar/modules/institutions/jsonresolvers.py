# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Institution resolver."""

from __future__ import absolute_import, print_function

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


# the host corresponds to the config value for the key JSONSCHEMAS_HOST
@jsonresolver.route("/api/institutions/<pid>", host="sonar.ch")
def institution_resolver(pid):
    """Resolve referenced institution."""
    resolver = Resolver(
        pid_type="inst", object_type="rec", getter=Record.get_record
    )
    _, record = resolver.resolve(pid)

    del record["$schema"]
    return record
