# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Test organisations API."""

from sonar.modules.organisations.api import OrganisationRecord


def test_get_organisation_by_user(user):
    """Test getting organisation by user."""
    # No user passed
    organisation = OrganisationRecord.get_organisation_by_user(None)
    assert not organisation

    # OK
    organisation = OrganisationRecord.get_organisation_by_user(user)
    assert 'code' in organisation
    assert organisation['code'] == 'org'

    user.pop('organisation')

    # User has no organisation
    organisation = OrganisationRecord.get_organisation_by_user(user)
    assert not organisation
