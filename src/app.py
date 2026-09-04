"""app.py - NIST TraCR Distribution Explorer Notebook.

This notebook explores how one community-resilience indicator is distributed
across counties in a single year, using NIST Tracking Community Resilience
(TraCR) data. It is also a teaching template: fork it, re-point
s00_nist_tracr_adapter.py at a different dataset, and the rest of the pipeline
and renderers keep working.

PLAN CELLS
1. Imports
2. Opening title and introduction (Markdown)
3. Load and process the data
4. Controls: indicator, renderer, mode
5. Controls: year available for the selected indicator
6. Build distribution result and the renderer-facing view
7. Render: one chart, or all stacked for comparison
8. Closing (Markdown)
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
async def _():
    import sys

    import altair as alt
    import marimo as mo
    import matplotlib.pyplot as plt
    import polars as pl

    if sys.platform == "emscripten":
        import micropip

        await micropip.install(["plotly", "pyarrow"])

    import plotly.express as px

    from s00_nist_tracr_adapter import load_raw
    from s01_process_data import process
    from s02_analytics import (
        get_distribution,
        list_indicators,
        list_years_for_indicator,
    )
    from s03_views import make_distribution_view
    from s04_charts_altair import make_altair_distribution
    from s04_charts_matplotlib import make_matplotlib_distribution
    from s04_charts_plotly import make_plotly_distribution

    return (
        get_distribution,
        list_indicators,
        list_years_for_indicator,
        load_raw,
        make_altair_distribution,
        make_distribution_view,
        make_matplotlib_distribution,
        make_plotly_distribution,
        mo,
        process,
    )


@app.cell
def _(mo):
    mo.md("""
    # NIST TraCR Community Distributions

    Pick an indicator and a year, and see how that indicator is distributed
    across all reporting counties.

    Choose one **renderer**, or switch to **Compare all** to see the same
    view rendered differently.
    """)
    return


@app.cell
def _(load_raw, mo, process):
    tracr_path = mo.notebook_location() / "public" / "TraCR_v1_database.csv"

    metadata_path = (
        mo.notebook_location() / "public" / "TraCR_Metadata_Column_Metadata.csv"
    )
    geography_path = mo.notebook_location() / "public" / "all-geocodes-v2020.csv"
    processed = process(
        load_raw(
            tracr_path,
            metadata_path=metadata_path,
            geography_path=geography_path,
        )
    )

    # return the processed data for further use
    return (processed,)


@app.cell
def _(list_indicators, mo, processed):
    indicators = list_indicators(processed)

    indicator = mo.ui.dropdown(
        options={name: indicator_id for indicator_id, name in indicators},
        value=indicators[0][1],
        label="Indicator",
    )

    renderer = mo.ui.dropdown(
        options=["Altair", "Plotly", "Matplotlib"],
        value="Altair",
        label="Renderer",
    )

    mode = mo.ui.radio(
        options=["Single", "Compare all"],
        value="Single",
        label="Mode",
    )

    # Indicator, renderer, and mode live together so changing renderer or mode
    # does not rerun the year cell below and reset the selected year.
    mo.vstack(
        [
            indicator,
            mo.hstack([renderer, mode], gap=1, justify="start"),
        ],
        gap=1,
        align="start",
    )

    # return the selected indicator, mode, and renderer for further use
    return indicator, mode, renderer


@app.cell
def _(indicator, list_years_for_indicator, mo, processed):
    years = list_years_for_indicator(processed, indicator.value)

    # Latest year is the most useful default snapshot of the distribution.
    year = mo.ui.dropdown(
        options={str(y): y for y in years},
        value=str(years[-1]),
        label="Year",
    )

    # display
    year

    # return the selected year for further use
    return (year,)


@app.cell
def _(get_distribution, indicator, make_distribution_view, processed, year):
    result = get_distribution(
        processed,
        indicator_id=indicator.value,
        year=year.value,
    )
    view = make_distribution_view(result)

    # return the view for further use
    return (view,)


@app.cell
def _(
    make_altair_distribution,
    make_matplotlib_distribution,
    make_plotly_distribution,
    mo,
    mode,
    renderer,
    view,
):
    def render_one(name):
        if name == "Altair":
            chart = make_altair_distribution(view)
            return mo.as_html(chart)  # not mo.ui.altair_chart(chart) which could be too big
        elif name == "Plotly":
            chart = make_plotly_distribution(view)
            return mo.ui.plotly(chart)
        elif name == "Matplotlib":
            chart = make_matplotlib_distribution(view)
            return mo.as_html(chart)

    if mode.value == "Compare all":
        output = mo.vstack(
            [render_one(name) for name in ["Altair", "Plotly", "Matplotlib"]],
            gap=2,
        )
    else:
        output = render_one(renderer.value)

    # display
    output

    # return the output for further use
    return


@app.cell
def _(mo):
    mo.md("""
    ## Suggestions

    - **Improve `s01`.** Processing is deliberately minimal.
      Add handling for suppressed values, revised indicators, or missing years.
      Document decisions.
    - **Add an analytic.** Median, spread, percentile summaries, or outlier
      counts can be new functions in `s02` returning their own small result
      types.

    [Source](https://github.com/civic-interconnect/distribution-tracr)
    """)
    return


if __name__ == "__main__":
    app.run()
