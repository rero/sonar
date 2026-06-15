# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations API."""

from sonar.modules.organisations.api import OrganisationRecord, OrganisationSearch


def test_get_or_create(organisation, search_clear):
    """Test get or create an organisation."""
    # Existing organisation
    organisation = OrganisationRecord.get_or_create("org", "Organisation")
    assert organisation["pid"] == "org"
    assert organisation["name"] == "org"

    # New organisation
    organisation = OrganisationRecord.get_or_create("new-org", "Organisation")
    assert organisation["pid"] == "new-org"
    assert organisation["name"] == "Organisation"


def test_get_shared_or_dedicated_list(organisation):
    """Test get list."""
    # Only shared
    records = OrganisationSearch().get_shared_or_dedicated_list()
    assert len(records) == 1
    assert records[0].to_dict() == {
        "pid": "org",
        "name": "org",
        "isDedicated": False,
        "isShared": True,
    }

    # Only dedicated
    organisation["isShared"] = False
    organisation["isDedicated"] = True
    organisation.commit()
    organisation.reindex()
    records = OrganisationSearch().get_shared_or_dedicated_list()
    assert len(records) == 1
    assert records[0].to_dict() == {
        "pid": "org",
        "name": "org",
        "isDedicated": True,
        "isShared": False,
    }

    # Shared and dedicated
    organisation["isShared"] = True
    organisation["isDedicated"] = True
    organisation.commit()
    organisation.reindex()
    records = OrganisationSearch().get_shared_or_dedicated_list()
    assert len(records) == 1
    assert records[0].to_dict() == {
        "pid": "org",
        "name": "org",
        "isDedicated": True,
        "isShared": True,
    }

    # Not shared not dedicated
    organisation["isShared"] = False
    organisation["isDedicated"] = False
    organisation.commit()
    organisation.reindex()
    records = OrganisationSearch().get_shared_or_dedicated_list()
    assert not records
