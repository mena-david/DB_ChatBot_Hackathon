import openai
import pinecone
import constants
from db import *
from flask import Flask, request, jsonify
import yaml

def read_yaml_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config
config_file = "config.yml"
config = read_yaml_config(config_file)

app = Flask(__name__)

# Set the OpenAI API key and client
openai.organization = config["api"]["openai-org"]
openai.api_key = config["api"]["openai"]
openai.Engine.list()

pinecone.init(
    api_key=config["api"]["pinecone"],
    environment="asia-northeast1-gcp"  # find next to API key in console
)

MODEL = "text-embedding-ada-002"

def setUpIndex():
    # Context Set up
    contex_items = constants.contex_items

    index = pinecone.Index('db-chatbot-personal')

    batch_num = 0
    batches = []
    for i in range(0, len(contex_items)):
        batch_text = contex_items[i]

        res = openai.Embedding.create(
            input=batch_text, engine="text-embedding-ada-002"
        )

        embedding = res.data[0].embedding
        id = 'batch' + '_' + str(batch_num)
        meta = {'text': batch_text}

        batches.append((id, embedding, meta))
        batch_num += 1

    index.upsert(vectors=batches)

    return index

#index = setUpIndex() #only needs to be done once
index = pinecone.Index('db-chatbot-personal')

def generate_gpt_response(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": context},
                      {"role": "user", "content": prompt}],
            max_tokens=170,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in generate_gpt_response: {e}")
        return "I'm sorry, but I couldn't complete your request. Please try again later."

def process_user_input(user_input, connection):
    xq = openai.Embedding.create(input=user_input, engine=MODEL)['data'][0]['embedding']
    res = index.query([xq], top_k=9, include_metadata=True)

    context = (
        "You are a chatbot whose main purpose is to extract data from a Database using SQL queries. Here are some facts to keep in mind. "
        "The Database ONLY has the following tables: users, organizations, organization_subscriptions, organization_members, plans, runs, entities, projects, alerts and alerts_subscriptions. "
    )

    schemas = "Here are the necessary database schema definitions for the different tables and all the available columns. Only refer to columns that exist on the schemas on the SQL query.\n"
    schemas += constants.DB_SHCEMA

    for match in res['matches']:
        #print(f"{match['score']:.2f}: {match['metadata']['text']}")
        context += str(match['metadata']['text'])

    prompt = f"{schemas}\nThe request is as follows: {user_input}\n Only output a SQL Query:\n"

    #print(prompt)

    sql_query = generate_gpt_response(prompt, context)

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query + "\n")
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)

        if not results:
            return "Sorry there was an error in executing the generated SQL query. Try rephrasing your question or indicating specific columns to refrence."

        print("Results from the Query/DB: " + str(results))
        # Prepare the response to display the results
        prompt = f"Based on this request by the user:'{user_input}' we ran this Database query '{sql_query}' which gave us the following results '{results}'. Format the results to be readable for the user"
        response_text = generate_gpt_response(prompt, "You are a helpful assistant")
    else:
        # If no SQL query was generated, ask GPT for a response
        response_text = generate_gpt_response(user_input, "You are a helpful assistant")

    return [response_text, sql_query]

def main_for_local_dev():
    # Connect to the database
    connection = connect_to_db()
    if not connection:
        print("Cannot connect to the database")
        return

    while True:
        try:
            # Get user input
            user_input = input("User: ")
            # Handle user input
            [response_text, query] = process_user_input(user_input, connection)
            print(f"Chatbot: {response_text}")
        except Exception as e:
            print("Error: ", e)
            break

    # Close the database connection
    connection.close()

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     connection = connect_to_db()
#     if not connection:
#         print("Cannot connect to the database")
#         return
#
#     user_input = request.json.get('user_input', '')
#     if not user_input:
#         return jsonify({'error': 'User input is required.'}), 400
#
#     response_text = process_user_input(user_input)
#
#     # Close the database connection
#     connection.close()
#
#     return jsonify({'response': response_text[0] + "  " + response_text[1] })
#
# if __name__ == '__main__':
#     #app.run(debug=True)
#     main_for_local_dev()
