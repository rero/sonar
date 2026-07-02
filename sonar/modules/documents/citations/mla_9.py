# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

from .base import BaseCitationStyle


class MLA9CitationStyle(BaseCitationStyle):
    """MLA 9th edition citation formatter."""

    style_id = "mla_9"
    style_label = "mla"
    style_version = "9th edition"

    def _format_authors(self, authors):
        """Format author list: first inverted, et al. for 3+."""
        if not authors:
            return ""
        if len(authors) >= 3:
            return authors[0][0] + ", et al."
        if len(authors) == 2:
            parts = [p.strip() for p in authors[1][0].split(",", 1)]
            second = " ".join(reversed(parts)) if len(parts) > 1 else authors[1][0]
            suffix = ", editors" if authors[0][1] else ""
            return authors[0][0] + ", and " + second + suffix
        suffix = ", editor" if authors[0][1] else ""
        return authors[0][0] + suffix

    def format(self, record, lang=None):
        """Return MLA 9th edition formatted citation."""
        authors = self._get_authors(record)
        author_str = self._format_authors(authors)
        full_title = self._get_full_title(record, lang)
        year, _place, publisher = self._get_publication(record)
        journal, volume, issue, pages = self._get_part_of(record)
        doi = self._get_doi(record)

        if journal:
            vol_issue = f"vol. {volume}" if volume else ""
            if issue:
                vol_issue += f", no. {issue}" if vol_issue else f"no. {issue}"
            pages_str = f", pp. {pages}" if pages else ""
            year_str = f", {year}" if year else ""
            doi_str = f", https://doi.org/{doi}" if doi else ""
            vol_issue_str = f", {vol_issue}" if vol_issue else ""
            return f'{author_str} "{full_title}." *{journal}*{vol_issue_str}{pages_str}{year_str}{doi_str}.'.strip()

        year_str = year or "n.d."
        return f"{author_str} *{full_title}*. {publisher or ''}, {year_str}.".strip()
