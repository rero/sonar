# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

from .base import BaseCitationStyle


class Chicago17CitationStyle(BaseCitationStyle):
    """Chicago/Turabian author-date citation formatter (17th edition)."""

    style_id = "chicago_17"
    style_label = "chicago"
    style_version = "17th edition"

    def _format_authors(self, authors):
        """Format author list: first author inverted, rest normal."""
        if not authors:
            return ""
        result = []
        for i, (name, _) in enumerate(authors):
            parts = [p.strip() for p in name.split(",", 1)]
            if i == 0:
                result.append(name)
            else:
                result.append(" ".join(reversed(parts)) if len(parts) > 1 else name)
        suffix = ", ed." if len(authors) == 1 and authors[0][1] else ", eds." if authors[0][1] else ""
        if len(result) == 1:
            return result[0] + suffix
        return ", ".join(result[:-1]) + ", and " + result[-1] + suffix

    def format(self, record, lang=None):
        """Return Chicago/Turabian author-date formatted citation (17th edition)."""
        authors = self._get_authors(record)
        author_str = self._format_authors(authors)
        full_title = self._get_full_title(record, lang)
        year, place, publisher = self._get_publication(record)
        journal, volume, issue, pages = self._get_part_of(record)
        doi = self._get_doi(record)

        year_str = year or "n.d."
        doi_str = f" https://doi.org/{doi}" if doi else ""

        if journal:
            vol_issue = volume or ""
            if issue:
                vol_issue += f", no. {issue}"
            pages_str = f": {pages}" if pages else ""
            return f'{author_str} {year_str}. "{full_title}." *{journal}* {vol_issue}{pages_str}.{doi_str}'.strip()

        place_publisher = f"{place}: {publisher}" if place and publisher else (publisher or place or "")
        return f"*{full_title}*. {author_str} {year_str}. {place_publisher}.{doi_str}".strip()
