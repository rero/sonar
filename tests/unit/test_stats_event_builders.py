# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test stats event builders."""

from sonar.stats_event_builders import flag_invalid_ip_as_robot


def test_flag_invalid_ip_as_robot():
    """Test that an event with a forged IP address is flagged as a robot."""
    assert flag_invalid_ip_as_robot({"ip_address": "'", "is_robot": False})["is_robot"]
    assert not flag_invalid_ip_as_robot({"ip_address": "93.184.216.34", "is_robot": False})["is_robot"]
