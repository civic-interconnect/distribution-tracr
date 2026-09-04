"""Tests for s02_analytics - the DistributionResult contract and its creation.

These exercise the analytics boundary directly on a small in-memory frame in
the canonical processed schema, so they need no data files and no network.
"""

import polars as pl
import pytest

from s02_analytics import (
    DistributionResult,
    get_distribution,
    list_indicators,
    list_years_for_indicator,
)


def make_processed() -> pl.DataFrame:
    """Return a tiny processed frame in the canonical long-form schema.

    Two indicators across three counties over two years, with one deliberate
    gap: indicator "i2" reports only in 2021. That lets the tests check
    per-indicator year filtering and the empty-selection error.
    """
    return pl.DataFrame(
        {
            "geography_id": ["01", "02", "03", "01", "02", "03", "01", "02"],
            "geography_name": [
                "Alpha County",
                "Bravo County",
                "Cerro County",
                "Alpha County",
                "Bravo County",
                "Cerro County",
                "Alpha County",
                "Bravo County",
            ],
            "indicator_id": ["i1", "i1", "i1", "i1", "i1", "i1", "i2", "i2"],
            "indicator_name": [
                "Employment rate",
                "Employment rate",
                "Employment rate",
                "Employment rate",
                "Employment rate",
                "Employment rate",
                "Broadband access",
                "Broadband access",
            ],
            "unit": [
                "percent",
                "percent",
                "percent",
                "percent",
                "percent",
                "percent",
                "percent",
                "percent",
            ],
            "year": [2020, 2020, 2020, 2021, 2021, 2021, 2021, 2021],
            "value": [61.0, 55.5, 48.2, 63.0, 57.1, 49.9, 80.0, 72.5],
        }
    )


def test_get_distribution_returns_result_type():
    """get_distribution returns a DistributionResult, not a bare frame."""
    result = get_distribution(make_processed(), indicator_id="i1", year=2020)
    assert isinstance(result, DistributionResult)


def test_get_distribution_filters_to_indicator_and_year():
    """Only rows for the requested indicator and year appear, one per county."""
    result = get_distribution(make_processed(), indicator_id="i1", year=2020)

    assert result.data.height == 3
    assert result.data.columns == ["geography_name", "value"]
    assert sorted(result.data["value"].to_list()) == [48.2, 55.5, 61.0]


def test_get_distribution_carries_semantics():
    """The result carries indicator name/id, unit, and the year it describes."""
    result = get_distribution(make_processed(), indicator_id="i1", year=2021)

    assert result.indicator_name == "Employment rate"
    assert result.indicator_id == "i1"
    assert result.unit == "percent"
    assert result.year == 2021


def test_get_distribution_sorted_by_geography_name():
    """Rows come back sorted by geography_name for stable display order."""
    result = get_distribution(make_processed(), indicator_id="i1", year=2020)

    names = result.data["geography_name"].to_list()
    assert names == sorted(names)


def test_get_distribution_data_holds_only_two_columns():
    """The renderer-bound data leaks no ids - only geography_name and value."""
    result = get_distribution(make_processed(), indicator_id="i1", year=2020)

    assert set(result.data.columns) == {"geography_name", "value"}


def test_get_distribution_empty_selection_raises():
    """A selection with no observations raises ValueError, never returns empty."""
    # indicator "i2" has no 2020 observations in the fixture.
    with pytest.raises(ValueError):
        get_distribution(make_processed(), indicator_id="i2", year=2020)


def test_get_distribution_unknown_indicator_raises():
    """An indicator absent from the data raises rather than returning empty."""
    with pytest.raises(ValueError):
        get_distribution(make_processed(), indicator_id="nope", year=2020)


def test_list_indicators_unique_and_sorted():
    """list_indicators returns unique (id, name) pairs sorted by name."""
    pairs = list_indicators(make_processed())

    assert pairs == [("i2", "Broadband access"), ("i1", "Employment rate")]


def test_list_years_for_indicator_ascending():
    """Years for an indicator come back unique and ascending."""
    assert list_years_for_indicator(make_processed(), "i1") == [2020, 2021]


def test_list_years_for_indicator_respects_indicator():
    """A sparser indicator reports only the years it actually has."""
    # "i2" only reports in 2021 in the fixture.
    assert list_years_for_indicator(make_processed(), "i2") == [2021]
