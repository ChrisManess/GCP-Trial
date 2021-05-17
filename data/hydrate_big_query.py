import os
from google.cloud import storage
from google.cloud import bigquery

# NOTICE: Was playing around with a concept here. It didn't pan out but I thought I'd leave the code in for now.
# TODO: Need to formalize this a bit better by replacing strings with env vars

storage_client = storage.Client()

bucket_name = "staging.torqata-coding-challenge.appspot.com"
destination_blob_name = "data/netflix_titles"
source_file_name = "./netflix_titles.csv"

bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(destination_blob_name)

blob.upload_from_filename(source_file_name)

print(
    "File {} uploaded to {}.".format(
        source_file_name, destination_blob_name
    )
)

client = bigquery.Client()

# TODO(developer): Set dataset_id to the ID of the dataset to create.
dataset_id = "{}.netflix".format(client.project)

# Construct a full Dataset object to send to the API.
dataset = bigquery.Dataset(dataset_id)

# TODO(developer): Specify the geographic location where the dataset should reside.
dataset.location = "US"

# Send the dataset to the API for creation, with an explicit timeout.
# Raises google.api_core.exceptions.Conflict if the Dataset already
# exists within the project.
# dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.

# show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
# for a first pass we'rd not going to put everything in the proper data stores we just want to get everything on platform and working

# TODO(developer): Set table_id to the ID of the table to create.
table_id = "torqata-coding-challenge.netflix.titles"

job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("show_id", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("director", "STRING"),
        bigquery.SchemaField("cast", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("date_added", "STRING"),
        bigquery.SchemaField("release_year", "NUMERIC"),
        bigquery.SchemaField("rating", "STRING"),
        bigquery.SchemaField("duration", "STRING"),
        bigquery.SchemaField("listed_in", "STRING"),
        bigquery.SchemaField("description", "STRING")
    ],
    skip_leading_rows=1,
    # The source format defaults to CSV, so the line below is optional.
    source_format=bigquery.SourceFormat.CSV,
)
uri = "gs://staging.torqata-coding-challenge.appspot.com/data/netflix_titles"

load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config
)  # Make an API request.

load_job.result()  # Waits for the job to complete.

destination_table = client.get_table(table_id)  # Make an API request.
print("Loaded {} rows.".format(destination_table.num_rows))
