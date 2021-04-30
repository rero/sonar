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

"""Validation API."""

from datetime import datetime

import pytz
from flask import current_app
from flask_babelex import _
from invenio_i18n.ext import current_i18n

from sonar.modules.users.api import UserRecord, current_user_record
from sonar.modules.users.exceptions import UserIsNotOwnerOfRecordError, \
    UserNotLoggedError, UserRecordNotFoundError
from sonar.modules.utils import send_email


class Status:
    """Enumeration for validation status."""

    IN_PROGRESS = 'in_progress'
    VALIDATED = 'validated'
    TO_VALIDATE = 'to_validate'
    REJECTED = 'rejected'
    ASK_FOR_CHANGES = 'ask_for_changes'


class Action:
    """Enumeration for validation action."""

    SAVE = 'save'
    PUBLISH = 'publish'
    APPROVE = 'approve'
    REJECT = 'reject'
    ASK_FOR_CHANGES = 'ask_for_changes'


class Validation:
    """Validation API."""

    def process(self, record):
        """Class initialization.

        :param record: Record to check.
        """
        # No validation we do nothing.
        if not record.get('metadata', {}).get('validation'):
            return

        # User cannot be loaded, we do nothing
        try:
            record_user = self._load_user(record)
        except Exception:
            return

        # Submitter user
        if not self._user_can_moderate():
            self._submitter_process(record, record_user)
        # Moderator
        else:
            self._moderator_process(record, record_user)

    def _submitter_process(self, record, user):
        """Process for submitter.

        :param record: Record object.
        :param user: User Record.
        """
        validation = record['metadata']['validation']

        # Save the record.
        if validation['action'] == Action.SAVE and validation['status'] in [
                Status.TO_VALIDATE, Status.VALIDATED
        ]:
            self._update_status(validation, Status.IN_PROGRESS)

        # Publish the record.
        if validation['action'] == Action.PUBLISH and validation['status'] in [
                Status.IN_PROGRESS, Status.ASK_FOR_CHANGES
        ]:
            self._update_status(validation, Status.TO_VALIDATE)
            # Send mail to moderators
            self._send_email(user.get_moderators_emails(),
                             Status.TO_VALIDATE,
                             record=record,
                             user=user,
                             app=current_app)

    def _moderator_process(self, record, user):
        """Process for moderator.

        :param record: Record object.
        :param user: User Record.
        """
        validation = record['metadata']['validation']

        # Save the record
        if validation['action'] == Action.SAVE:
            # Moderator is owner of the record. Record is published
            # directly.
            if self._user_is_owner_of_record(user):
                validation['status'] = Status.VALIDATED

        # Check all actions
        actions_map = {
            Action.ASK_FOR_CHANGES: Status.ASK_FOR_CHANGES,
            Action.REJECT: Status.REJECTED,
            Action.APPROVE: Status.VALIDATED
        }
        for action, status in actions_map.items():
            if validation['action'] == action and validation[
                    'status'] == Status.TO_VALIDATE:
                comment = validation.get('comment')
                self._update_status(validation, status)
                # Send mail to user
                self._send_email([user['email']],
                                 status,
                                 user=user,
                                 moderator=current_user_record,
                                 record=record,
                                 app=current_app,
                                 comment=comment)

    def _load_user(self, record):
        """Check data integrity and load user.

        :param record: Record to check.
        :returns: User record.
        """
        if not current_user_record:
            raise UserNotLoggedError

        if not record['metadata'].get('validation', {}).get('user'):
            raise Exception('No user stored in record')

        record_user = UserRecord.get_record_by_ref_link(
            record['metadata']['validation']['user']['$ref'])

        if not record_user:
            raise UserRecordNotFoundError

        if not self._user_can_moderate() and not self._user_is_owner_of_record(
                record_user):
            raise UserIsNotOwnerOfRecordError

        return record_user

    def _user_is_owner_of_record(self, record_user):
        """Check if logged user is the owner of the record.

        :param record_user: Owner of the record.
        :returns: True is logged user is owner.
        """
        return record_user['pid'] == current_user_record['pid']

    def _user_can_moderate(self):
        """Check if user can moderate the record.

        :returns: True is user is moderator.
        """
        return current_user_record and current_user_record.is_moderator

    def _update_status(self, validation, new_status):
        """Update status of the record.

        :param validation: Validation data of the record.
        :param new_status: New status.
        """
        validation['status'] = new_status

        user = current_user_record

        validation.setdefault('logs', [])
        validation['logs'].append({
            'status':
            validation['status'],
            'action':
            validation['action'],
            'user': {
                'pid': user['pid'],
                'name': f'{user["first_name"]} {user["last_name"]}'
            },
            'date':
            pytz.utc.localize(datetime.utcnow()).isoformat(),
            'comment':
            validation.get('comment')
        })

        # Clear comment.
        validation.pop('comment', None)

    def _send_email(self, recipients, email_type, **kwargs):
        """Send an email to concerned people.

        :param recipients: Send email to this list.
        :param email_type: Type of email.
        """
        if not isinstance(recipients, list) or not recipients:
            raise Exception('No recipients found in list')

        send_email(recipients, _('Record validation'),
                   f'validation/email/{email_type}', kwargs, False,
                   current_i18n.language)
