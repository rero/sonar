# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test SONAR views."""

import pytest
from flask import url_for


def test_error(client):
    """Test error page"""
    with pytest.raises(Exception):
        assert client.get(url_for("sonar.error"))
