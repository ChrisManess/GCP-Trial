# GCP-Trial

### Application Structure:

- Main.py does the orchestration of the application.
- Init.py does the largest part of the setup of the application, initializes settings and starts app.
- Models.py contains the information used to retreive the data from the database and serialize it through various points of the application

### Services Used:

CloudSQL, App Engine, Swagger(documentation), and Github

### Pain points/Regrets:

- Wish I hadn't spent time playing with bigquery initially, but new platform new toys.
- The way that the flask_sqlalchemy is a little different than just vanilla sqlalchemy and caused me to lose a bit of work time for the connection with CloudSQL.
- Using new service stacks is always an uphill battle at first, however GCP does have a lot of neat services
- Being locked out of the project because of accidently commiting json credentials to Github. (in hindsight I should've just deleted the repo and started over)
