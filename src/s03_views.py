"""s03_views.py - View preparation layer.

Turns a DistributionResult (analytics) into a DistributionView (presentation).

DistributionView is the contract every renderer consumes.
It holds what a distribution chart needs:

- the data
- which column holds the values to bin,
- how many bins to draw,
- the human-facing title and axis labels

A renderer never sees an indicator_id or a year.
"""

from dataclasses import dataclass

import polars as pl

from s02_analytics import DistributionResult


@dataclass(frozen=True)
class DistributionView:
    """Everything a renderer needs, and nothing it does not."""

    data: pl.DataFrame  # semantic columns kept: geography_name, value
    value_field: str  # "value" - the column to bin
    bins: int  # number of histogram bins
    title: str  # "Employment rate across counties (2020)"
    x_label: str  # "Percent" - what the value measures
    y_label: str  # "Number of counties" - the count axis


def make_distribution_view(result: DistributionResult) -> DistributionView:
    """Build the renderer-facing view from an analytics result."""
    return DistributionView(
        data=result.data,
        value_field="value",
        bins=30,
        title=f"{result.indicator_name} across counties ({result.year})",
        x_label=result.unit.title(),
        y_label="Number of counties",
    )
