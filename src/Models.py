from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from Init import app

# sqlalchemy instance
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Netflix(db.Model):
    show_id = db.Column(db.String(), primary_key=True)
    show_type = db.Column(db.String(), unique=True, nullable=False)
    title = db.Column(db.String(), unique=True, nullable=False)
    director = db.Column(db.String(), unique=True, nullable=False)
    cast = db.Column(db.String(), unique=True, nullable=False)
    country = db.Column(db.String(), unique=True, nullable=False)
    date_added = db.Column(db.String(), unique=True, nullable=False)
    release_year = db.Column(db.Integer, unique=True, nullable=False)
    rating = db.Column(db.String(), unique=True, nullable=False)
    duration = db.Column(db.String(), unique=True, nullable=False)
    listed_in = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), unique=True, nullable=False)


class NetflixSchema(ma.Schema):
    class Meta:
        fields = ("show_id", "show_type", "title", "director", "cast", "country",
                  "date_added", "release_year", "rating", "duration", "listed_in", "description")
        model = Netflix


netflix_schema = NetflixSchema()
neflixs_schema = NetflixSchema(many=True)
