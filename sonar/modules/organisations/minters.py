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

"""Persistent identifier minters for organisation."""

from __future__ import absolute_import, print_function, unicode_literals


def id_minter(record_uuid, data, provider, pid_key="pid", object_type="rec"):
    """Organisation minter which takes the code value as PID."""
    # Create persistent identifier
    provider = provider.create(
        object_type=object_type, object_uuid=record_uuid, pid_value=data.get("code")
    )

    pid = provider.pid
    data[pid_key] = pid.pid_value

    return pid
