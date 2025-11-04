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

"""Test project HEPVS rest API."""

import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_hepvs_list(app, client, project_hepvs_json, make_user, make_organisation, roles, submitter):
    """Test list projects permissions."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    make_organisation(code="hepvs", is_shared=False)
    user = make_user(
        role_name="moderator", organisation="hepvs", access="admin-access"
    )  # to cover dedicated schema import
    login_user_via_session(client, email=user["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(project_hepvs_json), headers=headers)
    assert res.status_code == 201
    # CSV format
    res = client.get(url_for("projects.search", format="text/csv"))
    assert res.status_code == 200
    assert (
        '"pid";"name";"approvalDate";"projectSponsor";"statusHep";"mainTeam";"innerSearcher";"secondaryTeam";"externalPartners";"status";"startDate";"endDate";"description";"keywords";"realizationFramework";"funding_funder_type";"funding_funder_name";"funding_funder_number";"funding_fundingReceived";"actorsInvolved";"benefits";"impactOnFormation";"impactOnProfessionalEnvironment";"impactOnPublicAction";"promoteInnovation";"relatedToMandate_mandate";"relatedToMandate_name";"relatedToMandate_briefDescription";"educationalDocument";"searchResultsValorised"'
        in res.data.decode()
    )
