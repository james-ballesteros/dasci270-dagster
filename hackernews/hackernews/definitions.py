from dagster import Definitions, load_assets_from_modules

from hackernews import assets  # noqa: TID252

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    resources={"local_csv_io_manager": assets.local_csv_io_manager}
)
