# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Institution Api."""


from functools import partial

from ..api import SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
InstitutionProvider = type(
    "InstitutionProvider", (Provider,), dict(pid_type="inst")
)
# minter
institution_pid_minter = partial(id_minter, provider=InstitutionProvider)
# fetcher
institution_pid_fetcher = partial(id_fetcher, provider=InstitutionProvider)


class InstitutionSearch(SonarSearch):
    """Search institutions."""

    class Meta:
        """Search only on item index."""

        index = "institutions"
        doc_types = []


class InstitutionRecord(SonarRecord):
    """Institution record class."""

    minter = institution_pid_minter
    fetcher = institution_pid_fetcher
    provider = InstitutionProvider
    schema = "institution"
