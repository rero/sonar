# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SONAR documents configuration."""

SONAR_DOCUMENTS_IMPORT_FILES = True
"""Import files associated with the document."""

SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT = True
"""Automatically extract fulltext when a file is imported."""

SONAR_DOCUMENTS_GENERATE_THUMBNAIL = True
"""Automatically generate a thumbnail when a file is imported."""

SONAR_DOCUMENTS_ORGANISATIONS_EXTERNAL_FILES = ["csal"]
"""Display external files URL for these organisations."""

SONAR_DOCUMENTS_PERMALINK = "{host}{org}/documents/{pid}"
"""Permalink for accessing documents details."""

SONAR_DOCUMENT_QUERY_BOOSTING = ["title.*^3", "fulltext^6", "*"]
"""Search query boosting parameters for documents."""
