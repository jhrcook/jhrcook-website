#!/usr/bin/env python3

"""Fill in the chart data for the running hobby page."""

import calendar
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Annotated, Final

import dateutil.parser
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
from rich.console import Console
from typer import Argument, Typer

app = Typer()
console = Console()
RUN_PAGE: Final[Path] = Path("./content/hobbies/running/index.md")
ADDITIONAL_RUNS_CSV: Final[Path] = Path(__file__).parent / "additional-runs.csv"
METERS_PER_MILE: Final[float] = 1609.344  # Number of meters in a mile.
SEC_PER_MIN: Final[int] = 60  # Number of seconds in a minute.


def set_style() -> None:
    sns.set_style("whitegrid")


def _parse_date(in_date: str) -> datetime:
    return dateutil.parser.parse(in_date)


def read_apple_export(file: Path) -> pl.DataFrame:
    return pl.read_csv(
        file, skip_rows=1, infer_schema_length=10000, dtypes={"sourceVersion": pl.Utf8}
    ).rename({"duration": "duration_seconds", "totalDistance": "distance_meters"})


def _load_additional_runs() -> pl.DataFrame:
    return read_apple_export(ADDITIONAL_RUNS_CSV)


def days_in_month(year: int, month: int) -> int:
    """Number of days in a month."""
    return calendar.monthrange(year, month)[1]


def plot_run_distance(
    running_data: pl.DataFrame, avg_running_data: pl.DataFrame, outfile: Path
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))

    avg_plot_data = (
        avg_running_data.rename(
            {
                "distance_per_week": "avg. distance per week",
                "avg_distance": "avg. distance per run",
            }
        )
        .melt(
            id_vars=["datetime"],
            value_vars=["avg. distance per week", "avg. distance per run"],
            variable_name="calc_label",
        )
        .to_pandas()
    )
    sns.lineplot(
        avg_plot_data,
        x="datetime",
        y="value",
        ax=ax,
        hue="calc_label",
        style="calc_label",
        alpha=1,
        markers={
            "avg. distance per week": "o",
            "avg. distance per run": "o",
        },
        dashes=False,
        zorder=10,
    )

    plot_data = running_data.to_pandas()
    sns.scatterplot(
        plot_data,
        x="startDate",
        y="distance_miles",
        ax=ax,
        c="black",
        s=5,
        alpha=1,
        edgecolor=None,
        zorder=20,
    )

    xax = ax.get_xaxis()
    xax.set_minor_locator(mpl_dates.MonthLocator())
    xax.set_minor_formatter(mpl_dates.DateFormatter("%b"))
    xax.set_major_locator(mpl_dates.YearLocator())
    xax.set_major_formatter(mpl_dates.DateFormatter("%Y"))
    ax.tick_params(axis="x", which="minor", rotation=90, labelsize=8, labelcolor="gray")
    ax.tick_params(axis="x", which="major", rotation=90, labelsize=10)

    sns.despine(ax=ax, left=True)
    ax.set_ylim(0, None)
    ax.set_xlabel("date")
    ax.set_ylabel("distance run (miles)")

    fig.tight_layout()
    fig.savefig(outfile, dpi=300)


def plot_pace(
    running_data: pl.DataFrame, avg_running_data: pl.DataFrame, outfile: Path
) -> None:
    ...


@app.command()
def main(
    running_data_export: Annotated[
        Path,
        Argument(
            help="Exported running data CSV.",
            file_okay=True,
            dir_okay=False,
            exists=True,
            readable=True,
        ),
    ],
) -> None:
    if not RUN_PAGE.exists():
        raise FileNotFoundError("Could not locate page for running hobby.")

    current_year = datetime.now().year
    current_month = datetime.now().month
    latest_year = current_year - 5
    console.log(f"Filtering data to after {latest_year}.")

    running_data = (
        pl.concat(
            [
                read_apple_export(running_data_export).drop("HKExternalUUID"),
                _load_additional_runs(),
            ],
            how="diagonal",
        )
        .with_columns(
            pl.col("startDate").map_elements(_parse_date),
            pl.col("endDate").map_elements(_parse_date),
            (pl.col("duration_seconds") / SEC_PER_MIN).alias("duration_minutes"),
            pl.col("distance_meters").str.replace(" m", "").cast(pl.Float64),
        )
        .with_columns(
            (pl.col("endDate") - pl.col("startDate")).alias("duration"),
            pl.col("startDate")
            .map_elements(lambda d: d.year, return_dtype=pl.Int64)
            .alias("year"),
            pl.col("startDate")
            .map_elements(lambda d: d.month, return_dtype=pl.Int64)
            .alias("month"),
            (pl.col("distance_meters") / METERS_PER_MILE).alias("distance_miles"),
        )
        .with_columns(
            (
                pl.col("duration").map_elements(lambda d: d.seconds / SEC_PER_MIN)
                / pl.col("distance_miles")
            ).alias("pace_min_per_mile")
        )
        .filter(latest_year < pl.col("year"))
    )

    avg_running_data = (
        running_data.group_by("month", "year").agg(
            pl.col("pace_min_per_mile").count().alias("count"),
            pl.col("pace_min_per_mile").mean().alias("avg_pace"),
            pl.col("distance_miles").sum().alias("total_distance"),
            pl.col("distance_miles").mean().alias("avg_distance"),
        )
    ).sort("year", "month")

    # Need to add in missing values for months where there were no runs.
    complete_dates = pl.DataFrame(
        product(avg_running_data["year"].unique(), avg_running_data["month"].unique())
    )
    complete_dates.columns = ["year", "month"]
    complete_dates = complete_dates.filter(
        (pl.col("year") < current_year) | (pl.col("month") < current_month)
    )
    avg_running_data = (
        complete_dates.join(avg_running_data, on=["year", "month"], how="left")
        .with_columns(
            pl.struct(["year", "month"])
            .map_elements(lambda d: datetime(d["year"], d["month"], 15))
            .alias("datetime"),
            pl.col("avg_distance").fill_null(0),
            pl.struct(["year", "month"])
            .map_elements(lambda x: days_in_month(x["year"], x["month"]))
            .alias("n_days"),
        )
        .with_columns(
            (pl.col("total_distance") / pl.col("n_days")).alias("distance_per_day")
        )
        .with_columns((pl.col("distance_per_day") * 7).alias("distance_per_week"))
    )
    console.print(avg_running_data)

    console.log("Plotting run distance.")
    plot_run_distance(
        running_data, avg_running_data, outfile=RUN_PAGE.parent / "distances.jpeg"
    )
    console.log("Plotting pace.")
    plot_pace(running_data, avg_running_data, outfile=RUN_PAGE.parent / "pace.jpeg")


if __name__ == "__main__":
    set_style()
    app()
