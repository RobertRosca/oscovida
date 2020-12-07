import datetime
import os
from pathlib import Path
from typing import List, Optional, Union

from fastcore.all import delegates

from .regions import Region

DROPPED_REGIONS = {
    'administrative_area_level_1': [
        'Costa Atlantica',
        'Cape Verde',
        'Diamond Princess',
        'Grand Princess',
    ],
    'administrative_area_level_2': [],
    'administrative_area_level_3': [],
}


@delegates()
class Index(Region):
    def __init__(
        self,
        country,
        admin_2: Optional[str] = None,
        admin_3: Optional[str] = None,
        columns: Optional[List] = None,
        **kwargs,
    ) -> None:
        kwargs['country'] = country
        kwargs['admin_2'] = admin_2
        kwargs['admin_3'] = admin_3

        super().__init__(**kwargs)

        if columns is None:
            self.columns = ["confirmed", "deaths", "population"]

        self.admin_area_level = f"administrative_area_level_{self.level}"
        self.admin_area_levels = [
            f"administrative_area_level_{level}" for level in range(1, self.level)
        ]

    def diff_dates(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        columns_delta: Optional[List] = None,
        normalize=False,
    ):
        #  TODO: Docstring, need to clarify the distinction between start and
        #  end dates passed through to the Region class via super init and the
        #  start and end dates used specifically for this method NB: start/end
        #  in init **filters data**, start/end here **defines the dates used for
        #  the difference calculation**
        if columns_delta is None:
            columns_delta = ["confirmed", "deaths"]

        data_start = self.data.loc[start.strftime("%Y%m%d")].set_index(
            self.admin_area_level
        )[self.columns + self.admin_area_levels]

        data_end = self.data.loc[end.strftime("%Y%m%d")].set_index(
            self.admin_area_level
        )[self.columns + self.admin_area_levels]

        data_delta = data_end[columns_delta] - data_start[columns_delta]
        data_delta = data_delta.rename(
            columns={
                "confirmed": "confirmed-delta",
                "deaths": "deaths-delta",
            }
        )

        data_index = data_end.join(data_delta)

        data_index = data_index.rename(
            columns={
                "confirmed": "confirmed-total",
                "deaths": "deaths-total",
            }
        )

        if normalize:
            data_index['confirmed-delta-per100k'] = (
                data_index['confirmed-delta'] / data_index['population'] * 100_000
            )
            data_index['deaths-delta-per100k'] = (
                data_index['deaths-delta'] / data_index['population'] * 100_000
            )

        self.index = data_index

        return self

    def diff_delta(self, delta_days: int = 7):
        #  TODO: I don't know if this is the best approach, delta here is the
        #  the latest available date - delta_days, not current data - delta_days
        #  which may be a bit unintuitive
        end = max(self.data.index)  # Set the max to the latest timestamp
        start = end - datetime.timedelta(delta_days)

        return self.diff_dates(start, end)

    def add_links(self, wwwroot: Union[str, Path], drop=True):
        if drop:
            self.index.drop(
                DROPPED_REGIONS[self.admin_area_level], axis='index', inplace=True
            )

        regions = self.index.index.to_list()

        for (i, r) in enumerate(regions):
            region = Region(r, lazy=True)
            path = region._path(wwwroot)
            regions[i] = f"[r]({path}" if os.path.exists(path) else r

        self.index.index = regions

        return self
