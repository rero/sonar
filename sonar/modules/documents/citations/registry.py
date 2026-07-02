# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Citation style registry."""


class CitationRegistry:
    """Registry that dispatches formatting to injected citation style classes."""

    def __init__(self, styles):
        """Register citation style instances keyed by their style_id.

        :param styles: Iterable of BaseCitationStyle instances.
        """
        self._styles = {style.style_id: style for style in styles}

    @property
    def supported_styles(self):
        """Return tuple of registered style identifiers."""
        return tuple(self._styles)

    def styles_info(self):
        """Return list of dicts with id and version for each registered style."""

        def _sort_key(s):
            # Sort by label alphabetically, then by numeric version (e.g. mla_9 before mla_10).
            version_num = int("".join(filter(str.isdigit, s["id"].split("_")[-1])) or 0)
            return (s["label"], version_num)

        return sorted(
            [{"id": s.style_id, "label": s.style_label, "version": s.style_version} for s in self._styles.values()],
            key=_sort_key,
        )

    def format(self, record, style, lang=None):
        """Return a formatted citation string for the given style.

        :param record: Document record dict.
        :param style: Style identifier string (e.g. 'apa').
        :param lang: Optional ISO 639-1 language code for title selection.
        :raises ValueError: If style is not registered.
        """
        if style not in self._styles:
            raise ValueError(f"Unsupported citation style '{style}'. Choose from: {', '.join(self.supported_styles)}")
        return self._styles[style].format(record, lang=lang)
