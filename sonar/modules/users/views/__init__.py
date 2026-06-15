# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for user module."""

from flask import Blueprint

blueprint = Blueprint("users", __name__, template_folder="../templates")
