"""Tests for s03_views - mapping a DistributionResult into a DistributionView.

These check the view contract: the fields a renderer reads, and that no
analytics-only identifiers (indicator_id, year) leak into the view.
"""

import polars as pl

from s02_analytics import DistributionResult
from s03_views import DistributionView, make_distribution_view


def make_result() -> DistributionResult:
    """Return a small DistributionResult to feed the view builder."""
    data = pl.DataFrame(
        {
            "geography_name": ["Alpha County", "Bravo County", "Cerro County"],
            "value": [61.0, 55.5, 48.2],
        }
    )
    return DistributionResult(
        data=data,
        indicator_name="Employment rate",
        indicator_id="i1",
        unit="percent",
        year=2020,
    )


def test_make_distribution_view_returns_view_type():
    """make_distribution_view returns a DistributionView."""
    view = make_distribution_view(make_result())
    assert isinstance(view, DistributionView)


def test_view_passes_data_through_unchanged():
    """The view carries the result's data frame unchanged."""
    result = make_result()
    view = make_distribution_view(result)

    assert view.data.columns == ["geography_name", "value"]
    assert view.data.height == 3


def test_view_value_field_points_at_value_column():
    """value_field names a column that actually exists in the data."""
    view = make_distribution_view(make_result())

    assert view.value_field == "value"
    assert view.value_field in view.data.columns


def test_view_title_names_indicator_and_year():
    """The title is human-facing and mentions the indicator and the year."""
    view = make_distribution_view(make_result())

    assert "Employment rate" in view.title
    assert "2020" in view.title


def test_view_x_label_is_titlecased_unit():
    """The x label presents the unit in title case (percent -> Percent)."""
    view = make_distribution_view(make_result())
    assert view.x_label == "Percent"


def test_view_y_label_is_count_axis():
    """The y label describes the count axis, not the measured value."""
    view = make_distribution_view(make_result())
    assert view.y_label == "Number of counties"


def test_view_has_positive_bin_count():
    """bins is a positive integer a histogram renderer can use directly."""
    view = make_distribution_view(make_result())

    assert isinstance(view.bins, int)
    assert view.bins > 0


def test_view_hides_analytics_identifiers():
    """The view exposes no indicator_id or year - renderers never see them."""
    view = make_distribution_view(make_result())

    assert not hasattr(view, "indicator_id")
    assert not hasattr(view, "year")
