# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Author Api."""


from functools import partial

from ..api import SonarRecord
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
AuthorProvider = type(
    'AuthorProvider',
    (Provider,),
    dict(pid_type='auth')
)
# minter
author_pid_minter = partial(id_minter, provider=AuthorProvider)
# fetcher
author_pid_fetcher = partial(id_fetcher, provider=AuthorProvider)


class AuthorRecord(SonarRecord):
    """Author record class."""

    minter = author_pid_minter
    fetcher = author_pid_fetcher
    provider = AuthorProvider
    schema = 'author'
