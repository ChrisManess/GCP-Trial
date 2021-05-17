import flask
from flask import request, jsonify
from flask import Flask
import uuid

from Init import app
from Models import Netflix, NetflixSchema, netflix_schema, neflixs_schema, db, ma


@app.route('/', methods=['GET'])
def home():

    return '''<h1>Movie and Shows Archive</h1>
              <p>Using titles from Netflix</p>
              <p><a href="/apidocs">API Documentation</a></p>'''

# TODO: Change data structure around where it matches this: {data item}.{source}


@app.route('/api/v1/titles/netflix/all', methods=['GET'])
def titles_all():
    """Returns a paginated list of all titles
    Allows you to retreive a paginated list of all titles in the database. Also allows you to tweak the pagnation properties
    ---
    parameters:
      - name: page
        in: path
        type: integer
        required: false
        default: 1
      - name: max
        in: path
        type: integer
        required: false
        default: 20
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/TitlesArray'
    """

    query_parameters = request.args

    page = int(query_parameters.get('page', 1))
    maximum = int(query_parameters.get('max', 20))

    titles = Netflix.query.paginate(page, maximum, error_out=False).items

    return jsonify(neflixs_schema.dump(titles))


@app.route('/api/v1/titles/netflix/search', methods=['GET'])
def titles_search():
    """Returns titles that match the search params
    Allows you to search across any one column.
    ---
    parameters:
      - name: field
        in: query
        type: string
        required: true
      - name: term
        in: query
        type: string
        required: true
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: max
        in: query
        type: integer
        required: false
        default: 20
    definitions:
      TitlesArray:
        type: array
        items:
          $ref: '#/definitions/Title'
      Title:
        type: object
        properties:
          cast:
            type: string
          country:
            type: string
          date_added:
            type: string
          description:
            type: string
          director:
            type: string
          duration:
            type: string
          listed_in:
            type: string
          rating:
            type: string
          release_year:
            type: integer
          show_id:
            type: string
          show_type:
            type: string
          title:
            type: string

    responses:
      200:
        description: A list of titles filtered on the field and term
        schema:
          $ref: '#/definitions/TitlesArray'
    """

    query_parameters = request.args

    page = int(query_parameters.get('page', 1))
    maximum = int(query_parameters.get('max', 20))

    try:
        field = query_parameters.get('field')
        term = query_parameters.get('term')
    except:
        abort(404)  # probably should have more descriptive errors here

    # probably not best to use these fields but it works and keeps me from needing another query
    available_fields = set(netflix_schema.Meta.fields)

    if field not in available_fields:
        abort(404)

    titles = Netflix.query.filter(getattr(Netflix, field).like(term)).all()

    return jsonify(neflixs_schema.dump(titles))

# TODO: Finish Documentation


@app.route('/api/v1/titles/netflix/releaseYear/count', methods=['GET'])
def title_year_count():
    """Returns the summary release titles by year
    Ordered by release year.
    ---
    definitions:
      ReleaseYearCountArray:
        type: array
        items:
          $ref: '#/definitions/ReleaseYearCountSummary'
      ReleaseYearCountSummary:
        type: object
        properties:
          release_year:
            type: int
          count:
            type: int
    responses:
      200:
        description: A list of release years with a count of how many titles were released that year
        schema:
          $ref: '#/definitions/ReleaseYearCountList'
    """

    query_parameters = request.args

    result = db.engine.execute(
        "SELECT release_year, count(*) AS released FROM netflix GROUP BY release_year ORDER BY release_year")

    release_year_count_list = [
        {"release_year": row[0], "count": row[1]} for row in result]

    return jsonify(release_year_count_list)


@app.route('/api/v1/titles/netflix/', methods=['Post'])
def add_title():
    """Creates a new titles record
    Creates a new titles record for a given JSON object input
    ---
    consumes:
      application/json
    parameters:
      - in: body
        name: title
        description: the title to add to the database
        schema:
          $ref: '#/definitions/Title'
    responses:
      200:
        description: the title that was created
        schema:
          $ref: '#/definitions/Title'
    """

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    object_uuid = str(uuid.uuid4())
    title_to_add = request.get_json()
    title = Netflix(
        # items in the database don't currently use UUID but I wanted to make sure all new items did
        show_id=object_uuid,
        title=title_to_add['title'],
        show_type=title_to_add['show_type'],
        director=title_to_add['director'],
        cast=title_to_add['cast'],
        country=title_to_add['country'],
        date_added=title_to_add['date_added'],
        release_year=title_to_add['release_year'],
        rating=title_to_add['rating'],
        duration=title_to_add['duration'],
        listed_in=title_to_add['listed_in'],
        description=title_to_add['description']
    )

    db.session.add(title)
    db.session.commit()

    return netflix_schema.dump(title)

# TODO: finish documentation here


@app.route('/api/v1/titles/netflix/<string:id>', methods=['GET'])
def get_title(id):
    """Gets a title record
    Gets the title by the id specified in the route
    ---
    consumes:
      application/json
    parameters:
      - name: id
        in: path
        type: string
        required: true
    responses:
      200:
        description: the title that corresponds to the id passed in the path 
        schema:
          $ref: '#/definitions/Title'
    """

    return netflix_schema.dump(Netflix.query.filter_by(show_id=id).first())

# TODO: finish documentation here


@app.route('/api/v1/titles/netflix/<string:id>', methods=['DELETE'])
def delete_title(id):
    """Deletes a title record
    Deletes the title by the id specified in the route
    ---
    consumes:
      application/json
    parameters:
      - name: id
        in: path
        type: string
        required: true
    definitions:
      CallStatus:
        type: object
        properties:
          status:
            type: string
    responses:
      200:
        description: the title that corresponds to the id passed in the path 
        schema:
          $ref: '#/definitions/CallStatus'
    """

    item_to_delete = Netflix.query.filter_by(show_id=id).first()

    if item_to_delete is not None:
        db.session.delete(item_to_delete)
        db.session.commit()

    return {"status": "success"}


@app.route('/api/v1/titles/netflix/<string:id>', methods=['Post'])
def update_title(id):
    """Updates a title record
    Updates a title record with the information passed in
    ---
    consumes:
      application/json
    parameters:
      - in: body
        name: title
        description: the title with information to be updated in the database
        schema:
          $ref: '#/definitions/Title'
    responses:
      200:
        description: the updated title
        schema:
          $ref: '#/definitions/Title'
    """

    title_to_update = Netflix.query.filter_by(show_id=id).first()

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    update_info = request.get_json()

    title_to_update.title = update_info['title'],
    title_to_update.show_type = update_info['show_type'],
    title_to_update.director = update_info['director'],
    title_to_update.cast = update_info['cast'],
    title_to_update.country = update_info['country'],
    title_to_update.date_added = update_info['date_added'],
    title_to_update.release_year = update_info['release_year'],
    title_to_update.rating = update_info['rating'],
    title_to_update.duration = update_info['duration'],
    title_to_update.listed_in = update_info['listed_in'],
    title_to_update.description = update_info['description']

    db.session.commit()

    return netflix_schema.dump(title_to_update)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True)
