## Data Pipelines of NY Taxi Data -  Using **Dagster** as Ochestrator

In this project, I created and orchestrated pipelines using Dagster as the ochestrator. 

My raw data source is [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).  
I used DuckDB as a database.  
I used the local file system to store some transformed data saved as CSVs and Parquet  
I used pandas and pyplot to analyse the data, generate charts and save them as PNGs in the local filesystem.

The completed Running pipeline is seen below
[Completed Pipeline from dagster-webserver](https://drive.google.com/file/d/1TvItsdPGodiejl6hR1-1nYGAroSteD2K/view?usp=sharing)


## Projects Description on how **dagster was utilized**
* Overall I had two data sources and three data sinks.  
With Dagster, I defined all sources,  sinks and external connections as [dagster resources](./dagster_university/resources/__init__.py)
* I defined each task as an [asset](./dagster_university/assets/) so they can be materialized independently and combined into jobs
* I made different [jobs](./dagster_university/jobs/__init__.py) from different combinations of assets in the pipeline so as to help schedule them at different intervals
* I used sensors for event driven orchestration. In this case, a particular jobs kicks of when a user uploads or modify a file in the [./data/requests/](./data/requests/) directory 
* I configured the sensors to run with different parameters depending on the contents of the file uploaded 
* I made my orchestration stateful by storing and retrieving tracking data from cursor property provided by the sensor context
