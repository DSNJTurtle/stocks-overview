"""Library."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pendulum
import tomlkit
import tomlkit.toml_file


@dataclass
class StocksDf:
    """Stock container."""

    wkn: str
    name: str
    qty: int
    buy_date: str
    sell_date: str | None = None


class StockOverview:
    """Stock overview class."""

    def __init__(self, config_path: str, stocks_file: str):
        self.config_path: str = config_path
        self.stocks_file: str = stocks_file
        self.stocks_df: pd.DataFrame | None = None
        self._missing_stocks_df()

    @classmethod
    def from_config_file(cls, config_path: Path) -> StockOverview:
        """
        Create a new StockOverview instance from existing config_path.

        Args:
            config_path: Path to existing config file.

        Returns: StocksOverview object

        """
        assert config_path.exists() and config_path.is_file()
        f = tomlkit.toml_file.TOMLFile(config_path)
        doc = f.read()
        so = StockOverview(doc["io"]["config_path"], doc["io"]["stocks_file"])
        return so

    def write_config_file(self) -> None:
        """
        Write current setup to config file.

        Returns: None

        """
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)

        io = tomlkit.table()
        io.add("config_path", self.config_path)
        io.add("stocks_file", self.stocks_file)
        doc = tomlkit.document()
        doc.add("io", io)

        tomlkit.toml_file.TOMLFile(self.config_path).write(doc)

    def write_stocks_df(self) -> None:
        """
        Write current setup to data file.

        Returns: None

        """
        assert self.stocks_df is not None
        self.stocks_df = self.stocks_df.fillna(value=np.nan)
        self.stocks_df.to_csv(self.stocks_file, header=True, index=False, na_rep="null")

    def is_wkn_known(self, wkn: str) -> bool:
        """
        Checks if WKN is already known.

        Args:
            wkn: WKN to look for

        Returns: True, if already present.

        """
        return not self.stocks_df.query(f"wkn=='{wkn}'").empty

    def get_name(self, wkn: str) -> str:
        """
        Get clear name for given WKN.

        Args:
            wkn: WKN to look for.

        Returns: Clear name of stock

        """
        assert self.is_wkn_known(wkn)
        return self.stocks_df.query(f"wkn=='{wkn}'").reset_index().at[0, "name"]

    def show_stocks(self, min_date: str = None) -> None:
        """
        Print current stock positions to console.

        Args:
            min_date: Only include already sold positions after this date.

        Returns: None

        """
        assert self.stocks_df is not None
        if min_date is None:
            min_date = start_of_year()

        if self.stocks_df.empty:
            print(self.stocks_df)
            return

        df = self.stocks_df
        mask = ((df["buy_date"] >= min_date) & (df["sell_date"].notna())) | (df["sell_date"].isna())
        df = df[mask].sort_values(["buy_date"])
        print(df)

    def add_stocks(self, wkn: str, name: str, qty: int, buy_date: str) -> None:
        """
        Add a new stock position.

        Args:
            wkn: WKN
            name: Clear name of stock
            qty: Quantity
            buy_date: Buy date.

        Returns: None

        """
        assert self.stocks_df is not None
        df = pd.DataFrame.from_records([asdict(StocksDf(wkn, name, qty, buy_date))])
        self.stocks_df = df if self.stocks_df.empty else pd.concat([self.stocks_df, df])
        self.stocks_df = self.stocks_df.reset_index(drop=True)
        self.write_stocks_df()
        print("Successfully added")

    def sell_stocks(self, wkn: str, qty: int, sell_date: str) -> None:
        """
        Sell some stock positions.

        Args:
            wkn: WKN
            qty: Quantity
            sell_date: Sell date

        Returns: None

        """
        other_stocks_df = self.stocks_df.query(f"wkn!='{wkn}' or sell_date.notnull()")
        wkn_df = self.stocks_df.query(f"wkn=='{wkn}' and sell_date.isnull()").sort_values(["buy_date"])
        remaining_stocks_to_sell = qty
        updates = []
        for row in wkn_df.itertuples(index=False):
            if remaining_stocks_to_sell <= 0:
                updates.append(row)
            else:
                n = row.qty
                new_n = n - remaining_stocks_to_sell
                if new_n <= 1e-4:
                    updates.append(row._replace(sell_date=sell_date))
                else:
                    updates.append(row._replace(qty=remaining_stocks_to_sell, sell_date=sell_date))
                    updates.append(row._replace(qty=new_n))

                remaining_stocks_to_sell = remaining_stocks_to_sell - n

        new_df = pd.DataFrame.from_records(updates, columns=[x for x in wkn_df.columns if x != "index"])
        new_df = other_stocks_df if new_df.empty else pd.concat([other_stocks_df, new_df])

        self.stocks_df = new_df.reset_index(drop=True)
        self.write_stocks_df()
        print("Successfully removed")

    def _missing_stocks_df(self) -> None:
        """
        Load or create the stock data file if not already present.

        Returns: None

        """
        if self.stocks_df is None:
            _p = Path(self.stocks_file)
            _p.parent.mkdir(parents=True, exist_ok=True)

            if _p.exists() and _p.is_file():
                self.stocks_df = pd.read_csv(self.stocks_file)
            else:
                print(f"{self.stocks_file} not present. Create default one.")
                d = {k: [] for k in asdict(StocksDf("abc", "def", 1, today_date()))}
                self.stocks_df = pd.DataFrame(d)
                self.stocks_df.to_csv(self.stocks_file, header=True, index=False, na_rep="null")


def today_date() -> str:
    """Returns: Get today's date as string."""
    return pendulum.now().date().to_date_string()


def start_of_year() -> str:
    """Returns: Get beginning of year as date string, e.g. 2024-01-01."""
    return pendulum.date(pendulum.now().year, 1, 1).to_date_string()
