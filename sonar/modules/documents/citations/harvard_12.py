# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

from .base import BaseCitationStyle


class Harvard12CitationStyle(BaseCitationStyle):
    """Harvard citation formatter (12th edition)."""

    style_id = "harvard_12"
    style_label = "harvard"
    style_version = "12th edition"

    def _format_authors(self, authors):
        """Format author list: Last, F. & Last, F. (eds.)."""
        if not authors:
            return ""
        formatted = [name for name, _ in authors]
        suffix = " (ed.)" if len(authors) == 1 and authors[0][1] else " (eds.)" if authors[0][1] else ""
        if len(formatted) == 1:
            return formatted[0] + suffix
        return ", ".join(formatted[:-1]) + " & " + formatted[-1] + suffix

    def format(self, record, lang=None):
        """Return Harvard formatted citation (12th edition)."""
        authors = self._get_authors(record)
        author_str = self._format_authors(authors)
        full_title = self._get_full_title(record, lang)
        year, place, publisher = self._get_publication(record)
        journal, volume, issue, pages = self._get_part_of(record)
        doi = self._get_doi(record)

        year_str = f"({year})" if year else "(n.d.)"
        doi_str = f", https://doi.org/{doi}" if doi else ""

        if journal:
            vol_issue = volume or ""
            if issue:
                vol_issue += f"({issue})"
            pages_str = f", pp. {pages}" if pages else ""
            return f"{author_str} {year_str} '{full_title}', *{journal}*, {vol_issue}{pages_str}{doi_str}.".strip()

        place_publisher = f"{place}: {publisher}" if place and publisher else (publisher or place or "")
        return f"{author_str} {year_str} *{full_title}*, {place_publisher}{doi_str}.".strip()
