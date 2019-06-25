# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test SONAR fetchers."""

import pytest

from sonar.modules.documents.api import DocumentRecord


def test_id_fetcher():
    """Test id fetcher."""
    assert DocumentRecord.fetcher("1", {"pid": "1"}).pid_value == "1"
