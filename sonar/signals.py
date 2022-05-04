# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Signals for SONAR."""

from blinker import Namespace
from flask import current_app

_signals = Namespace()

file_downloaded = _signals.signal('file-downloaded')
"""File downloaded signal."""

def file_download_proxy(obj):
    """This proxy add a sender to the original signal.

    TODO: this is a workaround that can be remove once invenio-stats has
          fixed some issues.
    """
    file_downloaded.send(current_app._get_current_object(), obj=obj)
