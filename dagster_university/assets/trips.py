import requests
from . import constants
from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource
from ..partitions import monthly_partition
import pandas as pd
import random


@asset(partitions_def=monthly_partition, group_name="raw_files")
def taxi_trips_file(context: AssetExecutionContext) -> MaterializeResult:
    """
    The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    partition_str = context.partition_key
    month_to_fetch = partition_str[:-3]
    print(month_to_fetch)
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)
    count = random.randint(5000, 9000)
    return MaterializeResult(
        metadata={
            "Number of Records": MetadataValue.int(count),
            "Number of people": MetadataValue.int(random.randint(11, 30)),
            "name": MetadataValue.text("Abdulshakur Muhammad Jamiu"),
            "attributes": MetadataValue.json({"age":29,"job":"software engineer"})
        }
    )

@asset(group_name="raw_files")
def taxi_zones_file() -> None:
    """Taxi Zones saved to file"""
    taxi_zones = requests.get('https://data.cityofnewyork.us/api/views/755u-8jsi/rows.csv?accessType=DOWNLOAD')
    with open(constants.TAXI_ZONES_FILE_PATH,'wb') as taxi_zones_csv:
        taxi_zones_csv.write(taxi_zones.content)
        

@asset(
    deps=["taxi_trips_file"],
    partitions_def=monthly_partition,
    group_name="ingested"
)
def taxi_trips(context: AssetExecutionContext, database: DuckDBResource) -> None:
    """
    The raw taxi trips dataset, loaded into a DuckDB database
    """
    partition_date_str = context.partition_key
    month_to_fetch = partition_date_str[:-3]

    sql_query = f"""
    create table if not exists trips (
        vendor_id integer, pickup_zone_id integer, dropoff_zone_id integer,
        rate_code_id double, payment_type integer, dropoff_datetime timestamp,
        pickup_datetime timestamp, trip_distance double, passenger_count double,
        total_amount double, partition_date varchar
    );

    delete from trips where partition_date = '{month_to_fetch}';

    insert into trips
    select
        VendorID, PULocationID, DOLocationID, RatecodeID, payment_type, tpep_dropoff_datetime,
        tpep_pickup_datetime, trip_distance, passenger_count, total_amount, '{month_to_fetch}' as partition_date
    from '{constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)}';
    """

    with database.get_connection() as conn:
        conn.execute(sql_query)



@asset(deps=['taxi_zones_file'], group_name="ingested")
def taxi_zones(database: DuckDBResource) -> None:
    """
    The raw taxi zones dataset, loaded into a DuckDB database
    """
    sql_query = f"""
        create or replace table zones as (
            select
            LocationID as zone_id,
            zone,
            borough,
            the_geom as geometry
    from '{constants.TAXI_ZONES_FILE_PATH}'
        );
    """

    with database.get_connection() as conn:
        conn.execute(sql_query)