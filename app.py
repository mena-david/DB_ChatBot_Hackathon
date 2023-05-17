from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from createSQL import *

app = Flask(__name__)

# curl -X POST -H "Content-Type: application/json" -d '{"message": "how many users do we have"}' http://127.0.0.1:5000/v1/chat
@app.route('/v1/chat', methods=['POST'])
def sql():
    connection = connect_to_db()
    if not connection:
        print("Cannot connect to the database")
        return

    req_data = request.get_json()
    if 'message' in req_data:
      message = req_data['message']
    else:
        return jsonify({'Error': 'User input is required.'}), 400

    sql_prompt = generate_sql_prompt(message)
    sql_query = generate_gpt_response(sql_prompt)
    sql_results = execute_query(sql_query, connection)

    text_prompt = f"Prepare a detailed response with the query '{sql_query}' human readable result '{sql_results}'"
    response = Response(stream_gpt_response(text_prompt), mimetype='text/event-stream')

    # Close the database connection
    connection.close()
    return response

# flask run
if __name__ == '__main__':
    print('is this app running?')
    app.run(debug=True)
    #main_for_local_dev()

CORS(app)
