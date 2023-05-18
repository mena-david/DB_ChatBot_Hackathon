from completion import *
from db import * 
import openai
import pinecone
import constants
from flask import Flask, request, jsonify
import yaml
import constants

def read_yaml_config(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config
config_file = "config.yml"
config = read_yaml_config(config_file)

db_config = config["database"]

# Set the OpenAI API key and client
openai.organization = config["api"]["openai-org"]
openai.api_key = config["api"]["openai"]
openai.Engine.list()

pinecone.init(
    api_key=config["api"]["pinecone"],
    # environment="us-central1-gcp"
    environment="asia-northeast1-gcp"  # find next to API key in console
)
pinecone_name = config["api"]["pinecone-name"]
# index = setUpIndex(pinecone_name) #only needs to be done once
index = pinecone.Index(pinecone_name)

embedding_model = config["api"]["embedding-model"]

def enrich_schema():
    schemas = "Here are the necessary database schema definitions for the different tables and all the available columns. Only refer to columns that exist on the schemas on the SQL query.\n"
    schemas += constants.DB_SCHEMA
    return schemas

def process_user_input(user_input, connection, stream=False):
    # Enrich context for generating the sql statement
    context = (
        "You are a chatbot whose main purpose is to extract data from a Database using SQL queries. Here are some facts to keep in mind. "
        "The Database ONLY has the following tables: users, organizations, organization_subscriptions, organization_members, plans, runs, entities, projects, alerts and alerts_subscriptions. "
    )
    xq = openai.Embedding.create(input=user_input, engine=embedding_model)['data'][0]['embedding']
    res = index.query([xq], top_k=9, include_metadata=True) # similarities
    for match in res['matches']:
        #print(f"{match['score']:.2f}: {match['metadata']['text']}")
        context += str(match['metadata']['text'])
    
    schemas = enrich_schema()
    sql_prompt = f"{schemas}\nThe request is as follows: {user_input}\n Only output a SQL Query:\n"    
    sql_query = generate_gpt_response(sql_prompt, context)

    # You may need to validate the generated SQL query before executing it on the database
    print(sql_query + "\n")
    if sql_query:
        # Execute the SQL query and get the results
        results = execute_query(sql_query, connection)
        if not results:
            return "Sorry there was an error in executing the generated SQL query. Try rephrasing your question or indicating specific columns to refrence."
        print("Results from the Query/DB: " + str(results))
        # print(results)
        # Prepare the response to display the results
        display_prompt = f"Prepare a human response with the query '{sql_query}' and result '{results}'"
        # display_prompt = f"Based on this request by the user:'{user_input}' we ran this Database query '{sql_query}' which gave us the following results '{results}'. Provide detailed human response"
        if stream:
            return stream_gpt_response(display_prompt, "You are a helpful assistant")
        else:
            return generate_gpt_response(display_prompt, "You are a helpful assistant")

    # If no SQL query was generated, ask GPT for a response
    return generate_gpt_response(user_input, "You are a helpful assistant")

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
            response_text = process_user_input(user_input, connection)
            print(f"Chatbot: {response_text}")
        except Exception as e:
            print("Error: ", e)
            break

    # Close the database connection
    connection.close()

if __name__ == '__main__':
    main_for_local_dev()
