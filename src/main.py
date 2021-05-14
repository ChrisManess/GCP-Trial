import os
import flask
from flask import request, jsonify
from google.cloud import bigquery
from flasgger import Swagger

app = flask.Flask(__name__)
swagger = Swagger(app)
app.config["DEBUG"] = True
DB_NAME = os.environ.get("DB_NAME")

@app.route('/', methods=['GET'])
def home():

    return '''<h1>Movie and Shows Archive</h1>
              <p>Using titles from Netflix</p>
              <p><a href="/apidocs">API Documentation</a></p>'''

def paginate_response(query, limit, offset, job_config=None):
    client = bigquery.Client()

    # might not be the best way to do things but lets me get away with what I wanted for now
    data_query = f"""
        SELECT * FROM ({query}) LIMIT {limit} OFFSET {offset}
    """

    if job_config is not None:
        data_query_job = client.query(data_query, job_config=job_config)
    else:
        data_query_job = client.query(data_query)

    data_results = data_query_job.result()

    return_list = []

    count_query = f"""
        SELECT count(*) FROM ({query})
    """
    count_query_job = client.query(count_query)
    count_results = count_query_job.result()

    total_record_count = 0

    for row in count_results:
        for items in row.items():
            total_record_count  = int(items[1])

    for row in data_results:
        data_item = {}

        for items in row.items():
            data_item[str(items[0])] = str(items[1])
        
        return_list.append(data_item)
    
    return {
        "count": total_record_count,
        "limit": limit,
        "start": offset,
        "items": return_list
    }

# TODO: Change data structure around where it matches this: {data item}.{source}
@app.route('/api/v1/titles/netflix/all', methods=['GET'])
def titles_all():
    """Returns a paginated list of titles
    Looked around at how other APIs are made and this seems to be a somewhat standard approach
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 100
      - name: offset
        in: query
        type: integer
        required: false
        default: 0
    definitions:
      PaginatedResponse:
        type: object
        properties:
          count:
            type: integer
          limit:
            type: integer
          start:
            type: integer
          items:
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
            type: string
          show_id:
            type: string
          title:
            type: string
          type:
            type: string
    responses:
      200:
        description: A paginated object containing items from the title 
        schema:
          $ref: '#/definitions/PaginatedResponse'
    """

    query_parameters = request.args

    limit = 100

    if "limit" in query_parameters:
        limit = int(query_parameters["limit"])

    offset = 0

    if "offset" in query_parameters:
        offset = int(query_parameters['offset'])

    titles = paginate_response("SELECT * FROM `torqata-coding-challenge.netflix.titles`", limit, offset)

    return jsonify(titles)

@app.route('/api/v1/titles/netflix/search', methods=['GET'])
def titles_search():
    query_parameters = request.args

    # this one will let users add their own bit to the query so lets use bigquery paramaterized queries to protect against injection

    limit = 100
    offset = 0

    client = bigquery.Client()

    field = "rating"
    
    field_query = f"""
        SELECT column_name
        FROM {DB_NAME}.netflix.INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = 'titles'
    """
    field_query_job = client.query(field_query)
    field_results = field_query_job.result()

    column_set = set()

    for row in field_results:
        for items in row.items():
            column_set.add(items[1])

    if field not in column_set:
        raise("Column not supported")

    #check that field to see if it's valid before adding and executing it. 
    query = f"""SELECT * FROM `{DB_NAME}.netflix.titles` WHERE {field} LIKE @term"""

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("term", "STRING", "G")
        ]
    )

    search_results = paginate_response(query, limit, offset, job_config=job_config)

    return jsonify(search_results)

# TODO: Finish Documentation
@app.route('/api/v1/titles/netflix/releaseYear/count', methods=['GET'])
def title_year_count():
    """Count of release years
    Paginated list of titles.
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 100
      - name: offset
        in: query
        type: integer
        required: false
        default: 0
    definitions:
      PaginatedResponse:
        type: object
        properties:
          count:
            type: integer
          limit:
            type: integer
          start:
            type: integer
          items:
            type: array
            items:
              $ref: '#/definitions/YearReleaseSummary'
      YearReleaseSummary:
        type: object
        properties:
          released:
            type: string
          release_year:
            type: string
    responses:
      200:
        description: A paginated object containing items from the title 
        schema:
          $ref: '#/definitions/YearReleaseSummary'
    """
    query_parameters = request.args

    limit = 200

    if "limit" in query_parameters:
        limit = int(query_parameters["limit"])

    offset = 0

    if "offset" in query_parameters:
        offset = int(query_parameters['offset'])

    years = paginate_response(f"SELECT release_year, count(*) AS released FROM `{DB_NAME}.netflix.titles` GROUP BY release_year ORDER BY release_year", limit, offset)

    return jsonify(years)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
