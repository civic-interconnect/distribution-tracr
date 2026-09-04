"""s04_charts_altair.py - Altair renderer.

One function, one contract:
make_altair_distribution(view) reads the field, bin count, and
labels from the view and returns an Altair chart.
"""

import altair as alt

from s03_views import DistributionView


def make_altair_distribution(view: DistributionView) -> alt.Chart:
    return (
        alt.Chart(view.data)
        .mark_bar()
        .encode(  # ty: ignore[unresolved-attribute]
            x=alt.X(
                f"{view.value_field}:Q",
                bin=alt.Bin(maxbins=view.bins),
                title=view.x_label,
            ),
            y=alt.Y("count()", title=view.y_label),
            tooltip=[alt.Tooltip("count()", title=view.y_label)],
        )
        .properties(title=view.title)
    )
