# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

from .base import BaseCitationStyle


class APA7CitationStyle(BaseCitationStyle):
    """APA 7th edition citation formatter."""

    style_id = "apa_7"
    style_label = "apa"
    style_version = "7th edition"

    def _format_authors(self, authors):
        """Format author list: Last, F., & Last, F. (Eds.)."""
        if not authors:
            return ""
        formatted = [name for name, _ in authors]
        suffix = " (Ed.)" if len(authors) == 1 and authors[0][1] else " (Eds.)" if authors[0][1] else ""
        if len(formatted) == 1:
            return formatted[0] + suffix
        return ", ".join(formatted[:-1]) + ", & " + formatted[-1] + suffix

    def format(self, record, lang=None):
        """Return APA 7th edition formatted citation."""
        authors = self._get_authors(record)
        author_str = self._format_authors(authors)
        full_title = self._get_full_title(record, lang)
        year, _place, publisher = self._get_publication(record)
        journal, volume, issue, pages = self._get_part_of(record)
        doi = self._get_doi(record)

        year_str = f"({year})" if year else "(n.d.)"
        doi_str = f" https://doi.org/{doi}" if doi else ""

        if journal:
            vol_issue = f", {volume}" if volume else ""
            if issue:
                vol_issue += f"({issue})"
            pages_str = f", {pages}" if pages else ""
            return f"{author_str} {year_str}. {full_title}. *{journal}*{vol_issue}{pages_str}.{doi_str}".strip()

        publisher_str = publisher or ""
        return f"{author_str} {year_str}. *{full_title}*. {publisher_str}.{doi_str}".strip()
