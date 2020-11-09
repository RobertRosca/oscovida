import datetime
from typing import List, Optional

from fastcore.all import delegates

from .regions import Region


@delegates()
class Index(Region):
    def __init__(self, country, columns: Optional[List] = None, **kwargs) -> None:
        kwargs['country'] = country

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
        normalize=True,
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
            data_index['confirmed-delta-p100k'] = (
                data_index['confirmed-delta'] / data_index['population'] * 100_000
            )
            data_index['deaths-delta-p100k'] = (
                data_index['deaths-delta'] / data_index['population'] * 100_000
            )

        return data_index

    def diff_delta(self, delta_days: int = 7):
        #  TODO: I don't know if this is the best approach, delta here is the
        #  the latest available date - delta_days, not current data - delta_days
        #  which may be a bit unintuitive
        end = max(self.data.index)  # Set the max to the latest timestamp
        start = end - datetime.timedelta(delta_days)

        return self.diff_dates(start, end)
