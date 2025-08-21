# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2025 RERO
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

"""Celery tasks for users."""

from celery import shared_task

from ..deposits.api import DepositRecord, DepositSearch


@shared_task()
def delete_deposits(user_pid, force=False, dbcommit=True, delindex=False):
    """Delete deposits for user.

    :param user_pid: User pid.
    :param force: True to hard delete record.
    :param dbcommit: True for validating database transaction.
    :param delindex: True to remove record from index.
    :returns: Count of deleted deposits.
    """
    query = DepositSearch().filter("term", user__pid=user_pid)
    count = 0
    for count, hit in enumerate(query.source("pid").scan()):
        deposit = DepositRecord.get_record_by_pid(hit.pid)
        deposit.delete(force=force, dbcommit=dbcommit, delindex=delindex)
    return count
