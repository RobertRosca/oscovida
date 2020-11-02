from functools import wraps
from typing import Optional, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from matplotlib.axes._axes import Axes
from matplotlib.ticker import ScalarFormatter

from .. import statistics

# choose font - can be deactivated
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Inconsolata']

# need many figures for index.ipynb and germany.ipynb
rcParams['figure.max_open_warning'] = 50

plt.style.use('ggplot')


COLOR_MAPPING = {
    'confirmed': {
        'totals': 'C1',
        'daily': 'C1',
        'r_number': 'C5',
        'growth_factor': 'C1',
        'doubling_time': 'C1',
    },
    'deaths': {
        'totals': 'C0',
        'daily': 'C0',
        'r_number': 'C4',
        'growth_factor': 'C0',
        'doubling_time': 'C0',
    },
}


def _standard_plot_formatting(plot_function):
    @wraps(plot_function)
    def formatted_plot(*args, **kwargs) -> Axes:
        ax = plot_function(*args, **kwargs)

        # labels on the right y-axis as well
        ax.tick_params(left=True, right=True, labelleft=True, labelright=True)
        ax.yaxis.set_ticks_position('both')
        ax.legend()

        return ax

    return formatted_plot


@_standard_plot_formatting
def plot_totals(
    series: pd.Series,
    ax: Optional[Axes] = None,
    color: Optional[str] = None,
    label_prepend: str = "",
    logscale: bool = True,
) -> Axes:
    """
    Plots the total numbers for a given series.

    Plots the input series assuming it is a cumulative sum of cases, deaths, or
    recoveries, either onto a new axis or onto a given axis. Plots follow the
    oscovida plotting style.

    Parameters:
        series : pd.Series
            Input data to plot, assumes it is a cumulative sum of `cases`, `deaths`,
            or `recovered`
        ax : Optional[Axes], optional
            Axes to plot onto, if `None` then defaults to `plt.gca()`
            By default `None`
        color : Optional[str], optional
            Color for the plot line, if `None` then the color is based on the series
            name, e.g. blue for cases, red for deaths
            By default `None`
        logscale : bool, optional
            If the plot should be log-y
            By default True
        label_prepend : [str], optional
            Label for the plotted line

    Returns:
        Axes
            Axes with plotted lines
    """
    if ax is None:
        ax = plt.gca()

    if color is None:
        color = COLOR_MAPPING[str(series.name)]['totals']

    ax.step(
        series.index,
        series,
        label=" ".join([label_prepend, f'total {series.name}']),
        color=color,
    )

    if logscale:
        ax.set_yscale('log')

    ax.yaxis.set_major_formatter(ScalarFormatter())

    ax.set_ylabel("total numbers")

    return ax


@_standard_plot_formatting
def plot_daily(
    series: pd.Series,
    ax: Optional[Axes] = None,
    color: Optional[str] = None,
    label_prepend: str = "",
    smoothing: str = 'weak',
) -> Axes:
    """
    Plots the daily numbers as a rolling average line, as well as a bar chart.

    Works out the daily numbers for a given input series assuming it is a
    cumulative sum of either `cases`, `deaths`, or `recoveries`. Plots a line
    with the smoothed daily numbers, and uses the raw numbers for a bar chart.

    Parameters:
        series : pd.Series
            Input data to plot, assumes it is a cumulative sum of `cases`, `deaths`,
            or `recovered`
        ax : Optional[Axes], optional
            Axes to plot onto, if `None` then defaults to `plt.gca()`
            By default `None`
        color : Optional[str], optional
            Color for the plot line, if `None` then the color is based on the series
            name, e.g. blue for cases, red for deaths
            By default `None`
        label_prepend : [type], optional
            String to prepend to the label, e.g. "GB" would make the labels "GB cases"
            and "GB deaths", instead of just generic "cases" and "deaths". This is
            automatically added when using a Region as an argument, must be manually
            added when passing a series
            By default `""`
        smoothing : str, optional
            Smoothing argument to use, see `oscovida.statistics.smooth` and
            `oscovida.statistics.SMOOTHING_METHODS` for more info
            By default 'weak'

    Returns:
        Axes
            Axes with plotted lines
    """
    if ax is None:
        ax = plt.gca()

    if color is None:
        color = COLOR_MAPPING[str(series.name)]['daily']

    bar_alpha = 0.2

    series_daily = series.pipe(statistics.daily)
    series_daily_s = series_daily.pipe(statistics.smooth, kind=smoothing)

    ax.bar(
        series_daily.index,
        series_daily.values,
        label=" ".join([label_prepend, f'new {series.name}']),
        color=color,
        alpha=bar_alpha,
    )

    ax.plot(
        series_daily_s.index,
        series_daily_s.values,
        label=" ".join(
            [label_prepend, f'new {series.name}', f"'{smoothing}' smoothing"]
        ),
        color=color,
    )

    ax.set_ylabel('daily change')

    return ax


@_standard_plot_formatting
def plot_r_number(
    series: pd.Series,
    ax: Optional[Axes] = None,
    color: Optional[str] = None,
    label_prepend: str = "",
    smoothing: str = '7dayrolling',
    yaxis_auto_lim: bool = True,
) -> Axes:
    """
    Plots the daily r number for a given series.

    Works out the daily numbers, applies smoothing, then computes the r number.

    This is then plotted along with a horizontal black line at a y axis value of 1.

    Parameters:
        series : pd.Series
            Input data to plot, assumes it is a cumulative sum of `cases`, `deaths`,
            or `recovered`
        ax : Optional[Axes], optional
            Axes to plot onto, if `None` then defaults to `plt.gca()`
            By default `None`
        color : Optional[str], optional
            Color for the plot line, if `None` then the color is based on the series
            name, e.g. blue for cases, red for deaths
            By default `None`
        label_prepend : [type], optional
            String to prepend to the label, e.g. "GB" would make the labels "GB cases"
            and "GB deaths", instead of just generic "cases" and "deaths". This is
            automatically added when using a Region as an argument, must be manually
            added when passing a series
            By default `""`
        smoothing : str, optional
            Smoothing argument to use, see `oscovida.statistics.smooth` and
            `oscovida.statistics.SMOOTHING_METHODS` for more info
            By default '7dayrolling'
        yaxis_auto_lim : bool, optional
            Uses `oscovida.statistics.min_max` to work out the minimum and maximum
            r number for the past 28 days, limits the y-axis to that range
            By default True

    Returns:
        Axes
            Axes with plotted lines
    """
    if ax is None:
        ax = plt.gca()

    if color is None:
        color = COLOR_MAPPING[str(series.name)]['r_number']

    r_number = (
        series.pipe(statistics.daily)
        .pipe(statistics.smooth, kind=smoothing)
        .pipe(statistics.r_number)
    )

    ax.plot(
        r_number,
        label=" ".join([label_prepend, f'{series.name} daily R number ({smoothing})']),
        color=color,
    )

    if yaxis_auto_lim:
        y_auto_min, y_auto_max = r_number.pipe(statistics.min_max, n=28)
        ax.set_ylim(y_auto_min, y_auto_max)

    ax.plot([series.index.min(), series.index.max()], [1.0, 1.0], '-C3')

    ax.set_ylabel(f'r number')

    return ax


@_standard_plot_formatting
def plot_growth_factor(
    series: pd.Series,
    ax: Optional[Axes] = None,
    color: Optional[str] = None,
    label_prepend: str = "",
    smoothing: str = '7dayrolling',
    yaxis_auto_lim: bool = True,
) -> Axes:
    """
    Plots the daily growth factor for a given series.

    Works out the daily numbers for a given input series assuming it is a
    cumulative sum of either `cases`, `deaths`, or `recoveries`. Smooths the
    data, then computes the growth factor. Plots a line for the growth factor
    and a line at y = 0.

    Parameters:
        series : pd.Series
            Input data to plot, assumes it is a cumulative sum of `cases`, `deaths`,
            or `recovered`
        ax : Optional[Axes], optional
            Axes to plot onto, if `None` then defaults to `plt.gca()`
            By default `None`
        color : Optional[str], optional
            Color for the plot line, if `None` then the color is based on the series
            name, e.g. blue for cases, red for deaths
            By default `None`
        label_prepend : [type], optional
            String to prepend to the label, e.g. "GB" would make the labels "GB cases"
            and "GB deaths", instead of just generic "cases" and "deaths". This is
            automatically added when using a Region as an argument, must be manually
            added when passing a series
            By default `""`
        smoothing : str, optional
            Smoothing argument to use, see `oscovida.statistics.smooth` and
            `oscovida.statistics.SMOOTHING_METHODS` for more info
            By default '7dayrolling'
        yaxis_auto_lim : bool, optional
            Uses `oscovida.statistics.min_max` to work out the minimum and maximum
            r number for the past 28 days, limits the y-axis to that range
            By default True

    Returns:
        Axes
            Axes with plotted lines
    """
    if ax is None:
        ax = plt.gca()

    if color is None:
        color = COLOR_MAPPING[str(series.name)]['growth_factor']

    growth_factor = series.pipe(statistics.smooth, kind=smoothing).pipe(
        statistics.growth_factor
    )

    ax.plot(
        growth_factor,
        label=" ".join(
            [label_prepend, f'{series.name} daily growth factor ({smoothing})']
        ),
        color=color,
    )

    if yaxis_auto_lim:
        y_auto_min, y_auto_max = growth_factor.pipe(statistics.min_max, n=28)
        ax.set_ylim(y_auto_min, y_auto_max)

    ax.plot([series.index.min(), series.index.max()], [1.0, 1.0], '-C3')

    ax.set_ylabel(f'growth factor')

    return ax


@_standard_plot_formatting
def plot_doubling_time(
    series: pd.Series,
    ax: Optional[Axes] = None,
    color: Optional[str] = None,
    label_prepend: str = "",
    smoothing: str = 'strong',
    yaxis_auto_lim: bool = True,
    logscale: bool = True,
) -> Axes:
    """
    Plots the doubling time for a given series.

    Works out the doubling time and plots it as a scatter plot, then smooths the
    doubling times and plots a rolling average as a line.

    Parameters:
        series : pd.Series
            Input data to plot, assumes it is a cumulative sum of `cases`, `deaths`,
            or `recovered`
        ax : Optional[Axes], optional
            Axes to plot onto, if `None` then defaults to `plt.gca()`
            By default `None`
        color : Optional[str], optional
            Color for the plot line, if `None` then the color is based on the series
            name, e.g. blue for cases, red for deaths
            By default `None`
        label_prepend : [type], optional
            String to prepend to the label, e.g. "GB" would make the labels "GB cases"
            and "GB deaths", instead of just generic "cases" and "deaths". This is
            automatically added when using a Region as an argument, must be manually
            added when passing a series
            By default `""`
        smoothing : str, optional
            Smoothing argument to use, see `oscovida.statistics.smooth` and
            `oscovida.statistics.SMOOTHING_METHODS` for more info
            By default 'strong'
        yaxis_auto_lim : bool, optional
            Uses `oscovida.statistics.min_max` to work out the minimum and maximum
            r number for the past 28 days, limits the y-axis to that range
            By default True

    Returns:
        Axes
            Axes with plotted lines
    """
    if ax is None:
        ax = plt.gca()

    if color is None:
        color = COLOR_MAPPING[str(series.name)]['daily']

    doubling_time = series.pipe(statistics.doubling_time)

    ax.plot(
        doubling_time.pipe(statistics.smooth, kind=smoothing),
        label=" ".join([label_prepend, f'{series.name} doubling time ({smoothing})']),
        color=color,
    )

    ax.plot(
        doubling_time,
        'o',
        alpha=0.3,
        label=" ".join([label_prepend, f'{series.name} doubling time']),
        color=color,
    )

    if yaxis_auto_lim:
        y_auto_min, y_auto_max = doubling_time.pipe(statistics.min_max, n=28)
        ax.set_ylim(y_auto_min, y_auto_max)

    if logscale:
        ax.set_yscale('log')

    return ax
