# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test SONAR extension."""

from sonar.modules.ext import Sonar


def test_init(app):
    """Test extension constructor."""
    sonar = Sonar(app)
    assert isinstance(sonar, Sonar)
