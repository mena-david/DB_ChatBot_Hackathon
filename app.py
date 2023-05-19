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

    response = Response(process_user_input(user_input=message, connection=connection, stream=True), mimetype='text/event-stream')

    # Close the database connection
    connection.close()
    return response

# flask run
if __name__ == '__main__':
    #app.run(debug=True)
    main_for_local_dev()

CORS(app)
