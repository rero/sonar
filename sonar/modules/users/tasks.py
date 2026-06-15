# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Celery tasks for users."""

from celery import shared_task

from ..deposits.api import DepositRecord, DepositSearch


@shared_task()
def delete_deposits(user_pid, force=False, dbcommit=False, delindex=False):
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
