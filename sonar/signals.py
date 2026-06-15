# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Signals for SONAR."""

from blinker import Namespace
from flask import current_app

_signals = Namespace()

file_downloaded = _signals.signal("file-downloaded")
"""File downloaded signal."""


def file_download_proxy(sender, obj):
    """This proxy add a sender to the original signal.

    TODO: this is a workaround that can be remove once invenio-stats has
          fixed some issues.
    """
    file_downloaded.send(current_app._get_current_object(), obj=obj)
