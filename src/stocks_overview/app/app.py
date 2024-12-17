#!/usr/bin/env python3

import glob
from pathlib import Path
from typing import Dict, Tuple

import pyfiglet
import rich
import typer
from rich.table import Table

from stocks_overview.library.stocks_overview import (
    StockOverview,
    start_of_year,
    today_date,
)

APP_NAME = "stocks-overview"
app = typer.Typer()


@app.command()
def show_stocks(min_date: str = typer.Option(prompt="Drop sold stocks before", default_factory=start_of_year)) -> None:
    """
    Show your current stock positions.

    Args:
        min_date: Include only already sold positions after this date.

    Returns: None

    """
    init().show_stocks(min_date)


@app.command()
def add_stocks() -> None:
    """
    Add a new stock position.

    Returns: None

    """
    _so = init()
    d, table = existing_stocks(_so)
    print("Known stocks:")
    rich.print(table)
    no = int(typer.prompt("Enter the desired number. Use default to enter a new WKN", default="-1"))
    wkn = d[int(no)] if no >= 0 else typer.prompt("Insert WKN")
    name = _so.get_name(wkn) if _so.is_wkn_known(wkn) else typer.prompt("Please provide a clear name for this new WKN")
    qty = typer.prompt("Number of new stocks")
    buy_date = typer.prompt("Buy date", default=today_date())

    _so.add_stocks(wkn, name, qty, buy_date)
    _so.show_stocks()


@app.command()
def sell_stocks() -> None:
    """
    Sell some stock position.

    Returns: None

    """
    _so = init()
    d, table = existing_stocks(_so)

    print("Which stock did you sell?")
    rich.print(table)
    no = typer.prompt("Please enter the desired No.")
    wkn = d[int(no)]

    qty = int(typer.prompt("How many stocks did you sell?"))
    sell_date = typer.prompt("When did you sell the stocks?", default=today_date())
    typer.confirm(f"Are you sure to sell {qty} stocks of {wkn}?", abort=True)
    _so.sell_stocks(wkn, qty, sell_date)
    _so.show_stocks()


def existing_stocks(_so: StockOverview) -> Tuple[Dict, Table]:
    """
    List exinsting stocks.

    Args:
        _so: StockOverview object

    Returns:
        Dict and table of availablke stocks.

    """
    table = Table("No.", "WKN", "Name")
    d = {}
    for i, e in enumerate(_so.stocks_df[["wkn", "name"]].drop_duplicates().sort_values(["wkn"]).to_numpy()):
        table.add_row(str(i), str(e[0]), e[1])
        d[i] = str(e[0])

    return d, table


def init() -> StockOverview:
    """
    Initialise new setup.

    Returns: StocksOverview object
    """
    app_dir = Path(typer.get_app_dir(APP_NAME))
    if app_dir.exists():
        config_file = glob.glob(str(app_dir / "*.toml"))
        if len(config_file) == 1:
            return StockOverview.from_config_file(Path(config_file[0]))
        else:
            raise RuntimeError(f"Found multiple config files {config_file}")

    # create default if not present
    print("Looks like you are running the program for the first time. Need to create relevant directories.")
    use_known_app_dir = typer.confirm(f"Do you want to use the default location {app_dir}?")
    new_app_dir = typer.get_app_dir(APP_NAME) if use_known_app_dir else typer.prompt("Path to new app directory")
    new_app_dir = Path(new_app_dir)
    new_app_dir.mkdir(parents=True, exist_ok=True)

    files_in_default_dir = typer.confirm("Do you want to create the data files in the same app directory?")
    new_files_dir = new_app_dir if files_in_default_dir else Path(typer.prompt("Path to new files directory"))
    new_files_dir.mkdir(parents=True, exist_ok=True)

    stock_overview = StockOverview(str(new_app_dir / "stocks_overview.toml"), str(new_files_dir / "stocks.csv"))
    stock_overview.write_config_file()

    return stock_overview


if __name__ == "__main__":
    pyfiglet.print_figlet(APP_NAME)
    app()
