# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test project HEPVS rest API."""

import copy
import json

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


def test_hepvs_list(app, client, project_hepvs_json, make_user, make_organisation, roles, submitter):
    """Test list projects permissions."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    proj_json = copy.deepcopy(project_hepvs_json)
    make_organisation(code="hepvs", is_shared=False)
    user = make_user(
        role_name="moderator", organisation="hepvs", access="admin-access"
    )  # to cover dedicated schema import
    proj_json["metadata"]["user"] = {"$ref": f"https://sonar.ch/api/users/{user['pid']}"}
    proj_json["metadata"]["organisation"] = {"$ref": "https://sonar.ch/api/organisations/hepvs"}
    login_user_via_session(client, email=user["email"])
    res = client.post(url_for("projects.search"), data=json.dumps(proj_json), headers=headers)
    assert res.status_code == 201
    # CSV format
    res = client.get(url_for("projects.search", format="text/csv"))
    assert res.status_code == 200
    assert (
        '"pid";"name";"approvalDate";"projectSponsor";"statusHep";"mainTeam";"innerSearcher";"secondaryTeam";"externalPartners";"status";"startDate";"endDate";"description";"keywords";"realizationFramework";"funding_funder_type";"funding_funder_name";"funding_funder_number";"funding_fundingReceived";"actorsInvolved";"benefits";"impactOnFormation";"impactOnProfessionalEnvironment";"impactOnPublicAction";"promoteInnovation";"relatedToMandate_mandate";"relatedToMandate_name";"relatedToMandate_briefDescription";"educationalDocument";"searchResultsValorised"'
        in res.data.decode()
    )
