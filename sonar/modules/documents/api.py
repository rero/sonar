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

from ..api import SonarRecord
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
DocumentProvider = type(
    'DocumentProvider',
    (Provider,),
    dict(pid_type='doc')
)
# minter
document_pid_minter = partial(id_minter, provider=DocumentProvider)
# fetcher
document_pid_fetcher = partial(id_fetcher, provider=DocumentProvider)


class DocumentRecord(SonarRecord):
    """Document record class."""

    minter = document_pid_minter
    fetcher = document_pid_fetcher
    provider = DocumentProvider
    schema = 'document'

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create a document record."""
        if 'author_id' in data:
            data['author'] = {
                '$ref': 'https://{}/api/authors/{}'.format(
                            current_app.config.get('JSONSCHEMAS_HOST'),
                            data['author_id'])
            }

            del data['author_id']

        return super(DocumentRecord, cls).create(data, id_=id_, **kwargs)
