# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""User exceptions."""


class AuthenticatedUserError(Exception):
    """Exception concerning the authenticated user."""


class UserNotLoggedError(AuthenticatedUserError):
    """Error when user is not logged."""


class UserRecordNotFoundError(AuthenticatedUserError):
    """Error when record object corresponding to logged user is not found."""


class UserIsNotOwnerOfRecordError(AuthenticatedUserError):
    """Raised when the logged user has not the ownership of a record."""
