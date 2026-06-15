# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User record extensions."""

from .delete_deposit import DeleteDepositsExtension
from .remove_roles import DeleteRolesExtension

__all__ = (
    "DeleteDepositsExtension",
    "DeleteRolesExtension",
)
