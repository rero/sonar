# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Bibliographic citation formatting for documents."""

from .registry import CitationRegistry, citation_registry

__all__ = (
    "CitationRegistry",
    "citation_registry",
)
