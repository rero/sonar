# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""BORIS schema."""

from .openaire import OpenaireSchema


class BorisSchema(OpenaireSchema):
    """BORIS marshmallow schema."""
