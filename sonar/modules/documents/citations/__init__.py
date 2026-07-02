# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Bibliographic citation formatting for documents."""

from .apa_7 import APA7CitationStyle
from .chicago_17 import Chicago17CitationStyle
from .harvard_12 import Harvard12CitationStyle
from .mla_9 import MLA9CitationStyle
from .registry import CitationRegistry

#: Default registry with all built-in citation styles.
citation_registry = CitationRegistry(
    [
        APA7CitationStyle(),
        Chicago17CitationStyle(),
        MLA9CitationStyle(),
        Harvard12CitationStyle(),
    ]
)

__all__ = (
    "APA7CitationStyle",
    "Chicago17CitationStyle",
    "CitationRegistry",
    "Harvard12CitationStyle",
    "MLA9CitationStyle",
    "citation_registry",
)
