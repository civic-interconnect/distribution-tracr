"""s04_charts_matplotlib.py - Matplotlib renderer.

make_matplotlib_distribution(view) reads the field, bin count, and
labels from the view and returns a Matplotlib Figure.
"""

import matplotlib

matplotlib.use("Agg")  # safe default; the notebook/app decides how to display

import matplotlib.pyplot as plt

from s03_views import DistributionView


def make_matplotlib_distribution(view: DistributionView) -> plt.Figure:
    values = view.data[view.value_field].to_list()

    figure, axes = plt.subplots()
    axes.hist(values, bins=view.bins)
    axes.set_title(view.title)
    axes.set_xlabel(view.x_label)
    axes.set_ylabel(view.y_label)
    figure.tight_layout()
    return figure
