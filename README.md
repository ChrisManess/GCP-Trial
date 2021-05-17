# GCP-Trial

### Application Structure:

- Main.py does the orchestration of the application
- Init.py does the largest part of the setup of the application, initializes settings and starts app
- Models.py contains the information used to retreive the data from the database and serialize it through various points of the application
- Routes.py comtains the routes for the application and all the code needed for them to do their functions

### Services Used:

CloudSQL, App Engine, Swagger(documentation), and Github

### Deploying this in your account:

(this was somewhat rushed so follow at your own peril)

Create Project, instances, and database

```
projectName=Your-Project-Name
databaseName=DB-Name
generatedPassword=`openssl rand -base64 20`
gcloud projects create "--name=${projectName}" --quiet
gcloud projects list | grep $projectName | awk '{print $1}' | xargs -I {} gcloud config set project "{}"
gcloud services enable sqladmin.googleapis.com
gcloud sql instances create prod-instance  --database-version=POSTGRES_9_6 --cpu=2 --memory=8GiB  --zone=us-central1-a "--root-password=${generatedPassword}"
ipAddress=`gcloud sql instances describe prod-instance | grep "ipAddress:" | awk '{print $3}'`
connectionName=`gcloud sql instances describe ${instanceName} | grep connectionName | awk '{print $2}'`
projectID=`gcloud projects list | grep $projectName | awk '{print $1}'`
gcloud sql databases create $databaseName --instance=prod-instance
gcloud sql connect prod-instance --user=postgres
```

will be in the postgres cli for this next section

```
\connect databaseName;
CREATE TABLE netflix(
    "show_id" TEXT PRIMARY KEY NOT NULL,
    "type" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "director" TEXT,
    "cast" TEXT,
    "country" TEXT,
    "date_added" TEXT,
    "release_year" INT,
    "rating" TEXT,
    "duration" TEXT,
    "listed_in" TEXT,
    "description" TEXT
);
exit
```

Back to the regular CLI

```
bucketName=gs://netflix-data-${projectID}
bucketFileLocation=gs://netflix-data-${projectID}/netflix_titles.csv
gsutil mb $bucketName
gsutil cp ./data/netflix_titles.csv $bucketName
```

- Now go to the console for the db instance and go through the import flow.

- Once that's completed there is one manual tweak we need to do

```
gcloud sql connect prod-instance --user=postgres
\connect databaseName;
ALTER TABLE netflix RENAME COLUMN type TO show_type;
```

- Now we can begin to get everything in place to deploy our application

- The folowing commands will delete the .env file in src so be sure you're ready to do that

```
echo PASSWORD=$password > ./src/.env
echo PUBLIC_IP_ADDRESS=$ipAddress >> ./src/.env
echo DBNAME=$databaseName >> ./src/.env
echo PROJECT_ID=$projectID >> ./src/.env
echo INSTANCE_NAME=prod-instance >> ./src/.env
echo CONNECTION_NAME=$connectionName >> ./src/.env
```

You can check if everything is working by adding your ip to the connections in the instance and then trying to start the flask app locally

```
cd src
python main.py
```

- If that's successful you should be ready to deploy now.

- First you'll need to copy the variable values from .env to the app.yaml.

- Once you've done that you will be able to deploy using the following command:

```
gcloud app deploy
```

### Observations:

- The way that the flask_sqlalchemy is a little different than just vanilla sqlalchemy and caused me to lose a bit of work time for the connection with CloudSQL.
- Using new service stacks is always an uphill battle at first, however GCP does have a lot of neat services and plenty of available orchestration.
- Being locked out of the project because of accidently commiting json credentials to Github was both bad and good. It gave me the push I needed to see how much of the setup process I could put into a script. However in hindsight I should've just deleted the repo and started over since I was only one commit in when I made my mistake.
