"""s04_charts_plotly.py - Plotly renderer.

make_plotly_distribution(view) reads the field, bin count, and
labels from the view and returns a Plotly figure.

Values are pulled as a plain list.
"""

import plotly.graph_objects as go

from s03_views import DistributionView


def make_plotly_distribution(view: DistributionView) -> go.Figure:
    values = view.data[view.value_field].to_list()

    figure = go.Figure(go.Histogram(x=values, nbinsx=view.bins))
    figure.update_layout(
        title=view.title,
        xaxis_title=view.x_label,
        yaxis_title=view.y_label,
    )
    return figure
