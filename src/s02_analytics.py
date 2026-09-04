"""s02_analytics.py - Analytics layer.

Owns the DistributionResult contract and its creation.
DistributionResult is the boundary between analytics and visualization.
It contains the observations plus the semantics needed to read them.

Median, spread, percentiles, ranking, outlier counts are additional
analytics.
They get their own functions and their own small result types
when the application needs them.
They do NOT get added to DistributionResult.

Hard rule: this module imports no charting or notebook library.
"""

from dataclasses import dataclass

import polars as pl


@dataclass(frozen=True)
class DistributionResult:
    """The per-geography values of one indicator in one year, plus semantics.

    Data carries only what the distribution needs: columns `geography_name`
    and `value` - one row per geography that reported the indicator that year.

    Remaining fields carry the semantics needed to understand those numbers.
    """

    data: pl.DataFrame  # columns: geography_name (str), value (float)
    indicator_name: str  # human-readable NIST indicator name
    indicator_id: str  # stable source identifier
    unit: str  # "percent", "count", "index", ...
    year: int  # the single year the distribution describes


def get_distribution(
    processed: pl.DataFrame, indicator_id: str, year: int
) -> DistributionResult:
    """Ask how one indicator is distributed across geographies in one year.

    Filters the processed observations to the requested indicator and year and
    packages the per-geography values with their semantics.

    Args:
        processed: The processed DataFrame containing all observations.
        indicator_id: The ID of the indicator to filter by.
        year: The single year to describe.

    Returns:
        A DistributionResult holding one value per geography and its semantics.
    """
    subset = processed.filter(
        (pl.col("indicator_id") == indicator_id) & (pl.col("year") == year)
    ).sort("geography_name")

    if subset.is_empty():
        raise ValueError(
            f"No observations for indicator_id={indicator_id!r}, year={year!r}."
        )

    first = subset.row(0, named=True)
    data = subset.select(["geography_name", "value"])

    return DistributionResult(
        data=data,
        indicator_name=first["indicator_name"],
        indicator_id=first["indicator_id"],
        unit=first["unit"],
        year=year,
    )


def list_indicators(processed: pl.DataFrame) -> list[tuple[str, str]]:
    """Return (indicator_id, indicator_name) pairs present in the data.

    Args:
        processed: The processed DataFrame containing all observations.

    Returns:
        A list of tuples, each an indicator_id and its indicator_name.
    """
    rows = (
        processed.select(["indicator_id", "indicator_name"])
        .unique()
        .sort("indicator_name")
        .iter_rows()
    )
    return list(rows)


def list_years_for_indicator(processed: pl.DataFrame, indicator_id: str) -> list[int]:
    """Return the years that have observations for one indicator, ascending.

    Args:
        processed: The processed DataFrame containing all observations.
        indicator_id: The ID of the indicator to filter by.

    Returns:
        A sorted (ascending) list of years with at least one observation.
    """
    rows = (
        processed.filter(pl.col("indicator_id") == indicator_id)
        .select("year")
        .unique()
        .sort("year")
        .to_series()
        .to_list()
    )
    return rows
