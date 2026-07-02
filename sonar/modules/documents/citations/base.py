# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Base class for citation styles."""


class BaseCitationStyle:
    """Abstract base for bibliographic citation formatters."""

    #: Unique identifier for this style, e.g. 'apa_7'.
    style_id = None
    #: Style family label, e.g. 'apa'.
    style_label = None
    #: Human-readable version string, e.g. '7th edition'.
    style_version = None

    def format(self, record, lang=None):
        """Return a formatted citation string for the given document record.

        :param record: Document record dict.
        :param lang: Optional ISO 639-1 language code for title selection.
        """
        raise NotImplementedError

    # --- shared helpers ---

    def _get_title(self, record, lang=None):
        """Return the main title, optionally filtered by language."""
        for title_entry in record.get("title", []):
            main_titles = title_entry.get("mainTitle", [])
            if lang:
                for t in main_titles:
                    if t.get("language") == lang:
                        return t["value"]
            if main_titles:
                return main_titles[0]["value"]
        return ""

    def _get_subtitle(self, record, lang=None):
        """Return the subtitle, optionally filtered by language."""
        for title_entry in record.get("title", []):
            subtitles = title_entry.get("subtitle", [])
            if lang:
                for s in subtitles:
                    if s.get("language") == lang:
                        return s["value"]
            if subtitles:
                return subtitles[0]["value"]
        return ""

    def _get_full_title(self, record, lang=None):
        """Return title combined with subtitle when present."""
        title = self._get_title(record, lang)
        subtitle = self._get_subtitle(record, lang)
        return f"{title}: {subtitle}" if subtitle else title

    def _get_authors(self, record):
        """Return list of (preferred_name, is_editor) tuples.

        Falls back to editors when no creators are found.
        """
        creators = [c for c in record.get("contribution", []) if "cre" in c.get("role", [])]
        if creators:
            return [(c["agent"]["preferred_name"], False) for c in creators if c.get("agent", {}).get("preferred_name")]
        editors = [c for c in record.get("contribution", []) if "edt" in c.get("role", [])]
        return [(c["agent"]["preferred_name"], True) for c in editors if c.get("agent", {}).get("preferred_name")]

    def _get_publication(self, record):
        """Return (year, place, publisher) from provisionActivity."""
        for activity in record.get("provisionActivity", []):
            if activity.get("type") != "bf:Publication":
                continue
            year = (activity.get("startDate") or "")[:4] or None
            place = None
            publisher = None
            for stmt in activity.get("statement", []):
                label = stmt.get("label")
                value = label[0]["value"] if isinstance(label, list) and label else (label or {}).get("value")
                if stmt.get("type") == "bf:Place" and not place:
                    place = value
                elif stmt.get("type") == "bf:Agent" and not publisher:
                    publisher = value
            return year, place, publisher
        return None, None, None

    def _get_part_of(self, record):
        """Return (journal_title, volume, issue, pages) from partOf."""
        parts = record.get("partOf", [])
        if not parts:
            return None, None, None, None
        part = parts[0]
        return (
            part.get("document", {}).get("title"),
            part.get("numberingVolume"),
            part.get("numberingIssue"),
            part.get("numberingPages"),
        )

    def _get_doi(self, record):
        """Return DOI value if present."""
        for identifier in record.get("identifiedBy", []):
            if identifier.get("type") == "bf:Doi":
                return identifier["value"]
        return None
