"""
Module containing some generic statistics functions for use with Oscovida, we
currently provide the following functions:

- `daily`: Computes the daily change for the series
- `smooth`: Smooths the pandas series with a rolling average and mean
- `doubling_time`: Compute the doubling time for a given series by shifting the
   rows by one
- `r_number`: Calculate the R-number using a method similar to RKI
- `growth_factor`: Computes the growth factor for a series
- `min_max`: Given a time series, find the min and max values in the time series
   within the last n days
"""

import math
from functools import singledispatch
from typing import Tuple, Union

import numpy as np
import pandas as pd

SMOOTHING_METHODS = {
    'weak': (
        {
            'window': 9,
            'center': True,
            'win_type': 'gaussian',
            'min_periods': 1,
        },
        {
            'mean_std': 3,
        },
    ),
    'strong': (
        {
            'window': 4,
            'center': True,
            'win_type': 'gaussian',
            'min_periods': 1,
        },
        {
            'mean_std': 2,
        },
    ),
    '7dayrolling': (
        {
            'window': 7,
            'center': True,
            'win_type': 'gaussian',
            'min_periods': 7,
        },
        {
            'mean_std': 3,
        },
    ),
}


def daily(cumulative: pd.Series, drop_negative=True) -> pd.Series:
    """
    Computes the daily change for the series.

    Parameters:
        cumulative : pd.Series
            Input series of sorted cumulative daily numbers

    Returns:
        pd.Series
            Difference between rows

    Examples:
        TODO
    """
    daily = cumulative.diff()

    if drop_negative:
        daily[daily < 0] = np.nan

    return daily.dropna()


def smooth(obj: pd.Series, kind: str = 'weak', compound: bool = True) -> pd.Series:
    """
    Smooths the pandas series with a rolling average and mean.

    Parameters:
        obj : pd.Series
            Input series of cumulative or daily numbers
        kind : str, optional
            Smoothing approach, either `'weak'`, `'strong'`, or `'7dayrolling`', by
            default 'weak'. The names correspond to:
            - 'weak': ({'window': 9, 'center': True, 'win_type': 'gaussian', 'min_periods': 1}, {'mean_std': 3})
            - 'strong': ({'window': 4, 'center': True, 'win_type': 'gaussian', 'min_periods': 1}, {'mean_std': 2})
            - '7dayrolling': ({'window': 7, 'center': True, 'win_type': 'gaussian', 'min_periods': 7,}, {'mean_std': 3,},
        ),
        compound : bool
            If smoothing should be compounded, default to `True`. e.g. picking
            `strong` means that the data is first smoothed with `weak` smoothing,
            and `strong` smoothing is applied to the already smoothed data

    Returns:
        pd.Series
            Smoothed series

    Examples:
        TODO
    """

    if (kind == 'strong') & compound:
        obj = obj.rolling(**SMOOTHING_METHODS['weak'][0]).mean(
            std=SMOOTHING_METHODS['weak'][1]['mean_std']
        )

    res = obj.rolling(**SMOOTHING_METHODS[kind][0]).mean(
        std=SMOOTHING_METHODS[kind][1]['mean_std']
    )

    return res


def doubling_time(cumulative: pd.Series) -> pd.Series:
    """
    Compute the doubling time for a given series by shifting the rows by one.

    The doubling time equation is:

    ```
    (t2 - t1) * (ln(2)/ln(q2/q1))
    ```

    This function assumes that `t2 - t1 = 1`. The doubling time is computed
    between subsequent rows. If you want to change the compared periods that
    should be done before calling this function (e.g. compute the weekly mean
    then put that into this function and you will get the weekly doubling time).

    By default

    Parameters:
        cumulative : pd.Series
            Input series of (usually) sorted cumulative daily numbers, as you want
            to find the doubling time of the cumulative number of cases not daily
            number

    Returns:
    pd.Series
            Doubling time

    Examples:
        TODO
    """
    cumulative_shifted = cumulative.shift(1)  # Previous day

    dt = np.log(2) / np.log(cumulative / cumulative_shifted)

    return dt


def r_number(cumulative: pd.Series, tau: int = 4) -> pd.Series:
    """
    Calculate the R-number using a method similar to RKI[1]. Assumes that the
    input series is sorted cumulative daily numbers.

    [1] Robert Koch Institute: Epidemiologisches Bulletin 17 | 23 April 2020
    https://www.rki.de/DE/Content/Infekt/EpidBull/Archiv/2020/Ausgaben/17_20.html

    Parameters:
        cumulative : pd.Series
            Input series of sorted cumulative daily numbers
        tau : int, optional
            Day averages, by default 4

    Returns:
        pd.Series
            R number per-day
    """
    # TODO: Look at using method from:
    # https://www.medrxiv.org/content/10.1101/2020.04.19.20071886v2.full.pdf
    # http://trackingr-env.eba-9muars8y.us-east-2.elasticbeanstalk.com/
    # and
    # https://valeriupredoi.github.io/

    rolling_avg = cumulative.rolling(tau).mean()
    R = rolling_avg / rolling_avg.shift(tau)
    R2 = R.shift(-tau)

    R2[(rolling_avg.shift(tau) == 0.0) & (rolling_avg == 0)] = 1

    return R2


def growth_factor(obj: pd.Series) -> pd.Series:
    """
    Computes the growth factor for a series.

    Growth factor is just the percent change day-to-day, in this case we add one
    to get the growth, e.g. 20% more cases than yesterday means 1.2 (120%), or
    a 20% drop would be 0.8 (80%)

    Parameters:
        obj : pd.Series
            Input series of daily numbers

    Returns:
        pd.Series
            Growth factor
    """
    return obj.pct_change() + 1


def min_max(obj: pd.Series, n: int, at_least=(0.75, 1.25), alert=(0.1, 100)) -> Tuple:
    """
    Given a time series, find the min and max values in the time series
    within the last n days.

    If those values are within the interval `at_least`, then use the values in
    at_least as the limits. if those values are outside the interval `at_least`
    then exchange the interval accordingly.

    Parameters:
        obj : pd.Series
            Input series
        n : int
            Past number of days looked at
        at_least : tuple, optional
            by default (0.75, 1.25)
        alert : tuple, optional
            Currently not used, by default (0.1, 100)

    Returns:
        Tuple
            Tuple of (min, max)
    """
    if n > len(obj):
        n = len(obj)

    obj = obj.replace(math.inf, math.nan)

    # the -0.1 is to make extra space because the line we draw is thick
    min_ = obj[-n:].min() - 0.1
    max_ = obj[-n:].max() + 0.1

    if min_ < at_least[0]:
        min_final = min_
    else:
        min_final = at_least[0]

    if max_ > at_least[1]:
        max_final = max_
    else:
        max_final = at_least[1]

    #  TODO: Add alert logging

    return min_final, max_final
