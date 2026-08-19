# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test Elasticsearch configuration."""

from types import SimpleNamespace

import pytest

from sonar.config import (
    RECORDS_REST_FACETS,
    SONAR_APP_AGGREGATION_SHARD_SIZE,
    SONAR_APP_AGGREGATION_SIZE,
)
from sonar.ext import (
    _configure_default_terms_aggregation_sizes,
    _set_default_terms_aggregation_sizes,
)


def _find_terms_aggregations(value):
    """Find terms aggregations recursively in a configuration value."""
    if isinstance(value, dict):
        terms = value.get("terms")
        if isinstance(terms, dict):
            yield terms
        for nested_value in value.values():
            yield from _find_terms_aggregations(nested_value)
    elif isinstance(value, (list, tuple)):
        for nested_value in value:
            yield from _find_terms_aggregations(nested_value)


@pytest.mark.parametrize(
    ("configured_size", "configured_shard_size"),
    [
        (SONAR_APP_AGGREGATION_SIZE, SONAR_APP_AGGREGATION_SHARD_SIZE),
        (75, 2000),
    ],
)
def test_terms_aggregations_use_configured_sizes(configured_size, configured_shard_size):
    """Test that terms aggregations receive the configured size settings."""
    app = SimpleNamespace(
        config={
            "RECORDS_REST_FACETS": RECORDS_REST_FACETS,
            "SONAR_APP_AGGREGATION_SIZE": configured_size,
            "SONAR_APP_AGGREGATION_SHARD_SIZE": configured_shard_size,
        },
    )

    _configure_default_terms_aggregation_sizes(app)

    configured_terms = list(_find_terms_aggregations(app.config["RECORDS_REST_FACETS"]))
    default_terms = list(_find_terms_aggregations(RECORDS_REST_FACETS))

    assert configured_terms
    assert len(configured_terms) == len(default_terms)
    assert all("size" not in terms for terms in default_terms)
    assert all("shard_size" not in terms for terms in default_terms)
    for terms in configured_terms:
        assert terms["size"] == configured_size
        assert terms["shard_size"] == configured_shard_size


def test_default_terms_sizes_are_recursive_and_preserve_explicit_values():
    """Test nested terms and explicitly configured sizes."""
    aggregation = {
        "filters": {"query": {"terms": {"status": ["published"]}}},
        "aggs": {
            "default": {"terms": {"field": "author"}},
            "explicit_size": {"terms": {"field": "subject", "size": 25}},
            "explicit_shard_size": {"terms": {"field": "language", "shard_size": 250}},
            "histogram": {"date_histogram": {"field": "year"}},
            "filtered": {
                "filter": {"match_all": {}},
                "aggs": {"nested": {"terms": {"field": "collection"}}},
            },
        },
    }

    _set_default_terms_aggregation_sizes(aggregation, 50, 1000)

    aggregations = aggregation["aggs"]
    assert aggregations["default"]["terms"]["size"] == 50
    assert aggregations["default"]["terms"]["shard_size"] == 1000
    assert aggregations["explicit_size"]["terms"]["size"] == 25
    assert aggregations["explicit_size"]["terms"]["shard_size"] == 1000
    assert aggregations["explicit_shard_size"]["terms"]["size"] == 50
    assert aggregations["explicit_shard_size"]["terms"]["shard_size"] == 250
    assert "size" not in aggregations["histogram"]["date_histogram"]
    assert "shard_size" not in aggregations["histogram"]["date_histogram"]
    assert aggregations["filtered"]["aggs"]["nested"]["terms"]["size"] == 50
    assert aggregations["filtered"]["aggs"]["nested"]["terms"]["shard_size"] == 1000
    assert "size" not in aggregation["filters"]["query"]["terms"]
    assert "shard_size" not in aggregation["filters"]["query"]["terms"]
