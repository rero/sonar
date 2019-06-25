# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Document Api."""

from functools import partial

from flask import current_app

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
DocumentProvider = type("DocumentProvider", (Provider,), dict(pid_type="doc"))
# minter
document_pid_minter = partial(id_minter, provider=DocumentProvider)
# fetcher
document_pid_fetcher = partial(id_fetcher, provider=DocumentProvider)


class DocumentSearch(SonarSearch):
    """Search documents."""

    class Meta:
        """Search only on item index."""

        index = "documents"
        doc_types = []


class DocumentRecord(SonarRecord):
    """Document record class."""

    minter = document_pid_minter
    fetcher = document_pid_fetcher
    provider = DocumentProvider
    schema = "document"
