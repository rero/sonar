# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test PDF extractor extension."""

from sonar.modules.pdf_extractor.ext import PDFExtractor


def test_ext(app):
    """Test PDF extractor extension."""
    ext = PDFExtractor(app)
    assert isinstance(ext, PDFExtractor)
