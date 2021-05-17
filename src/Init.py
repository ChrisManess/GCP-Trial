import os
import flask
from flasgger import Swagger

app = flask.Flask(__name__)
swagger = Swagger(app)
app.config["DEBUG"] = True

PASSWORD = os.getenv('PASSWORD')
PUBLIC_IP_ADDRESS = os.getenv('PUBLIC_IP_ADDRESS')
DBNAME = os.getenv('DBNAME')
PROJECT_ID = os.getenv('PROJECT_ID')
INSTANCE_NAME = os.getenv('INSTANCE_NAME')
CONNECTION_NAME = os.getenv('CONNECTION_NAME')

DATABASE_URI = f"postgresql://postgres:{PASSWORD}@{PUBLIC_IP_ADDRESS}:5432/{DBNAME}"

if os.getenv('FLASK_ENV') != "development":
    DATABASE_URI += f"?host=/cloudsql/{CONNECTION_NAME}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
