# fmt: off
from dagster import Definitions, load_assets_from_modules
from .assets import metrics, trips, requests
from .resources import database_resource
from .jobs import weekly_update_job, trip_update_job, adhoc_request_job
from .schedules import weekly_update_schedule, trip_update_schedule
from .sensors import adhoc_request_sensor

jobs = [weekly_update_job, trip_update_job, adhoc_request_job]
schedules = [weekly_update_schedule, trip_update_schedule]
trip_assets = load_assets_from_modules([trips])
metric_assets = load_assets_from_modules([metrics])
request_assets = load_assets_from_modules(modules=[requests],group_name="requests")

defs = Definitions(
    assets=[*trip_assets, *metric_assets, *request_assets],
    resources={"database": database_resource},
    jobs=jobs,
    schedules=schedules,
    sensors=[adhoc_request_sensor]
)
